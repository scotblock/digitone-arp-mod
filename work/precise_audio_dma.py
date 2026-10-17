"""Audio arrivals and completion IRQ wakeups on the PC core-cycle timeline."""
import collections,heapq,math
from fractions import Fraction
from shared_dma_arbiter import SharedDmaMemory
from emu.pit import interrupt_level

class PreciseAudioMemory(SharedDmaMemory):
 def install_dma(self):
  self.audio_timing=collections.Counter();self.audio_records=[];self.irq_records=[]
  self.next_audio=None;self.request_at=None;self.event_at=None;self.irq_asserted_at=None
  super().install_dma()
  if not self.ssi:return
  self.audio_period=Fraction(self.clock.fsys,self.ssi.request_hz)
  if self.ssi.enabled:
   offset=getattr(self.session,'_t0',0)
   self.next_audio=self.ssi.next-offset if self.ssi.next is not None else Fraction(self.clock.cycles)+self.audio_period
  self.ssi.step=lambda done,remaining=None:None
  # The original SSI service would emit requests at its outer checkpoint.
  # Arrival generation belongs exclusively to the merged cycle event queue.
  self.ssi.service=lambda done:self.deliver_irqs()
  original_raise=self.m.raise_vector
  def raise_vector(vec,*args,**kwargs):
   before=self.clock.cycles;ok=original_raise(vec,*args,**kwargs)
   if ok and vec in (self.ssi.p.tx_vector,191):
    record=dict(vector=vec,attempt_cycle=before,entry_cycle=self.clock.cycles,
                assertion_cycle=self.irq_asserted_at if vec==self.ssi.p.tx_vector else None)
    if record['assertion_cycle'] is not None:
     delay=before-record['assertion_cycle'];self.audio_timing['completion_to_IRQ_attempt_max_cycles']=max(self.audio_timing['completion_to_IRQ_attempt_max_cycles'],delay)
    self.audio_timing[f'vector_{vec}_delivered']+=1
    if len(self.irq_records)<64:self.irq_records.append(record)
   return ok
  self.m.raise_vector=raise_vector

 def step(self,done,remaining=None):
  targets=[]
  if self.next_audio is not None:targets.append(math.ceil(self.next_audio))
  if self.events and self.active[self.events[0][2]['channel'].channel].get('ssi'):
   targets.append(self.events[0][0])
  if self.ssi and self.ssi.int50_asserted and not self.ssi.int50_delivered:
   if interrupt_level(self.m,self.ssi.p.tx_vector) is not None:targets.append(self.clock.cycles+1)
  if not targets:return None
  value=max(1,min(targets)-self.clock.cycles)
  return min(value,remaining) if remaining is not None else value

 def deliver_irqs(self):
  if not self.ssi:return
  if not self.ssi.int50_asserted:self.irq_asserted_at=None
  self.ssi._deliver_vector170();self.ssi._deliver_vector191()

 def service(self,done):
  self.service_payload();self.deliver_irqs()

 def advance(self,state,at,value=None):
  audio=state.get('ssi');ch=state['channel'].channel
  if audio and 'request_cycle' not in state:
   at=self.request_at if self.request_at is not None else at
   state['request_cycle']=at;state['deadline']=math.ceil(self.next_audio+self.audio_period) if self.request_at is not None else at+math.ceil(self.audio_period)
   # Determine IRQ eligibility before descriptor execution changes CITER.
   citer=self.ssi._u16(ch,20);biter=self.ssi._u16(ch,28);csr=self.ssi._u16(ch,30)
   state['completion_irq']=ch==self.ssi.p.tx_chan and bool((citer==1 and csr&2) or (citer-1==biter//2 and csr&4))
  previous=bool(self.ssi and self.ssi.int50_asserted);self.event_at=at
  super().advance(state,at,value)
  if audio and ch not in self.active:
   latency=at-state['request_cycle'];self.audio_timing['audio_completed']+=1
   self.audio_timing['request_to_completion_max_cycles']=max(self.audio_timing['request_to_completion_max_cycles'],latency)
   self.audio_timing['next_frame_deadline_misses']+=at>state['deadline']
   if state['completion_irq']:
    self.audio_timing['completion_IRQ_assertions']+=1
    if previous:self.audio_timing['completion_IRQ_coalesced']+=1
    else:self.irq_asserted_at=at
   if len(self.audio_records)<64:self.audio_records.append(dict(channel=ch,request=state['request_cycle'],completion=at,observed=self.clock.cycles,deadline=state['deadline'],completion_irq=state['completion_irq']))

 def service_payload(self):
  if self.servicing:return
  self.servicing=True
  try:
   if self.ssi and self.ssi.enabled and self.next_audio is None:
    self.next_audio=Fraction(self.clock.cycles)+self.audio_period
   while True:
    arrival=math.ceil(self.next_audio) if self.next_audio is not None and self.ssi and self.ssi.enabled else None
    payload=self.events[0][0] if self.events else None
    due=min(x for x in (arrival,payload) if x is not None) if arrival is not None or payload is not None else None
    if due is None or due>self.clock.cycles:break
    if arrival is not None and arrival==due:
     self.audio_timing['frames_requested']+=1;self.ssi.requests+=1
     self.audio_timing['arrival_service_lateness_max_cycles']=max(self.audio_timing['arrival_service_lateness_max_cycles'],self.clock.cycles-due)
     self.request_at=due;self.batching_audio=True
     try:
      self.request_ssi(self.ssi.p.rx_chan,False);self.request_ssi(self.ssi.p.tx_chan,True)
     finally:self.batching_audio=False;self.request_at=None
     self.dispatch(due);self.next_audio+=self.audio_period
     continue
    due,seq,state,op=heapq.heappop(self.events);kind,address,size,data=op
    if self.owner!=state['channel'].channel:raise RuntimeError('DMA event without controller ownership')
    self.observe_payload(kind,state,due)
    if kind=='write':self.dma_span(address,size,True);self.m.uc.mem_write(address,data);value=None
    elif kind in ('rxread','rxskip'):value=None
    else:self.dma_span(address,size,False);value=bytes(self.m.uc.mem_read(address,size))
    self.payload_counts[kind+'_beats']+=1
    self.payload_counts['service_lateness_cycles_max']=max(self.payload_counts['service_lateness_cycles_max'],self.clock.cycles-due)
    if len(self.payload_samples)<32:self.payload_samples.append(dict(channel=state['channel'].channel,kind=kind,address=hex(address),size=size,due=due,observed=self.clock.cycles))
    self.advance(state,due,value)
   if self.owner is None:self.dispatch(self.clock.cycles)
  finally:self.servicing=False

 def observe_payload(self,kind,state,due):
  pass

 def report(self):
  r=super().report();r['audio_event_timing']=dict(counts=dict(self.audio_timing),completions=self.audio_records,interrupts=self.irq_records,next_request=str(self.next_audio),period=str(self.audio_period) if self.ssi else None,limits=['CPU execution and visibility still basic-block granular','Interrupt delivery occurs at the first available scheduler boundary and obeys masking','Next-frame completion deadline is a proxy, not a physical codec FIFO model','Clock and memory costs remain assumed'])
  return r
