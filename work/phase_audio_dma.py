"""PC-only occupancy model, stock SSI1 FIFO0 configuration and shared DMA."""
import collections,heapq,math,struct,os
from fractions import Fraction
from precise_audio_dma import PreciseAudioMemory
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
class PhaseAudioMemory(PreciseAudioMemory):
 def install_dma(self):
  super().install_dma()
  self.fifo_counts=collections.Counter();self.fifo_samples=[]
  self.tx_level=14;self.rx_level=0;self.min_tx=14;self.max_rx=0
  self.phase_mode=os.environ.get('SSI_PHASE_POLICY','first-bit')
  self.status_due=None;self.tx_flag=False;self.rx_flag=False;self.error_flags=0
  self.status_flags=0;self.status_reads=0;self.status_writes=0
  self.shift_valid=True;self.shift_started=None;self.shift_finished=0
  self.word_period=self.audio_period/2
  self.bit_period=self.word_period/32
  self.next_word=self.next_audio-self.word_period if self.next_audio is not None else Fraction(self.clock.cycles)+self.word_period
  regs={i:struct.unpack('>I',self.m.uc.mem_read(0xfc0c8000+i,4))[0] for i in (0x10,0x18,0x1c,0x20,0x24,0x2c)}
  assert regs=={0x10:0x37,0x18:0x500000,0x1c:0xe8,0x20:0x488,0x24:0x16101,0x2c:0x22},regs
  self.fifo_config={hex(k):hex(v) for k,v in regs.items()}
  def read_status(uc,access,address,size,value,data):
   self.status_reads+=1;self.service_payload();self.publish_status()
  def ack_status(uc,access,address,size,value,data):
   self.status_writes+=1
   # Only model aligned full-width W1C writes; do not accept an unknown shape.
   if address!=0xfc0c8014 or size!=4:raise RuntimeError('Unsupported SSI status write shape')
   self.error_flags&=~(value&0x500);self.status_flags&=~(value&0x500)
  self.hooks.append(self.m.uc.hook_add(UC_HOOK_MEM_READ,read_status,begin=0xfc0c8014,end=0xfc0c8017))
  self.hooks.append(self.m.uc.hook_add(UC_HOOK_MEM_READ,read_status,begin=0xfc0c802c,end=0xfc0c802f))
  self.hooks.append(self.m.uc.hook_add(UC_HOOK_MEM_WRITE,ack_status,begin=0xfc0c8014,end=0xfc0c8017))
 def publish_status(self):
  uc=self.m.uc;old=int.from_bytes(uc.mem_read(0xfc0c8014,4),'big')
  uc.mem_write(0xfc0c8014,((old&~0x505)|self.status_flags).to_bytes(4,'big'))
  old=int.from_bytes(uc.mem_read(0xfc0c802c,4),'big')
  uc.mem_write(0xfc0c802c,((old&~0xff00)|(self.rx_level<<12)|(self.tx_level<<8)).to_bytes(4,'big'))
 def step(self,done,remaining=None):
  # Parent IRQ wakeup handling, but replace frame arrivals with word arrivals.
  old=self.next_audio;self.next_audio=min(x for x in (self.next_word,self.status_due) if x is not None)
  try:return super().step(done,remaining)
  finally:self.next_audio=old
 def request_levels(self,at):
  self.request_at=at;self.batching_audio=True
  try:
   for ch,tx,condition in [(self.ssi.p.rx_chan,False,self.rx_flag and self.rx_level>=2),(self.ssi.p.tx_chan,True,self.tx_flag and self.tx_level<=13)]:
    if condition and ch in self.ssi.enabled and ch not in self.active:
     self.fifo_counts['TX_requests' if tx else 'RX_requests']+=1
     if tx:self.tx_flag=False
     else:self.rx_flag=False
     self.request_ssi(ch,tx)
  finally:self.request_at=None;self.batching_audio=False
  self.dispatch(at)
 def advance(self,state,at,value=None):
  # Inherited frame-window diagnostics need this request's moving phase.
  # Actual FIFO faults remain the deadline criterion.
  old=self.next_audio
  if state.get('ssi') and 'request_cycle' not in state:
   self.next_audio=Fraction(self.request_at if self.request_at is not None else at)
  try:return super().advance(state,at,value)
  finally:self.next_audio=old
 def observe_payload(self,kind,state,due):
  if not state.get('ssi'):return
  ch=state['channel'].channel
  if ch==self.ssi.p.tx_chan and kind=='write':
   if self.tx_level==15:self.fifo_counts['TX_overflow']+=1
   else:self.tx_level+=1
  if self.tx_level>13:self.status_flags&=~1
  if ch==self.ssi.p.rx_chan and kind=='rxread':
   if self.rx_level==0:self.fifo_counts['RX_empty_read']+=1
   else:self.rx_level-=1
  if self.rx_level<2:self.status_flags&=~4
 def service_payload(self):
  if self.servicing:return
  self.servicing=True
  try:
   while True:
    arrival=math.ceil(self.next_word) if self.ssi.enabled else None
    payload=self.events[0][0] if self.events else None
    status=math.ceil(self.status_due) if self.status_due is not None else None
    if arrival is None and payload is None and status is None:break
    due=min(x for x in (arrival,payload,status) if x is not None)
    if due>self.clock.cycles:break
    if arrival==due:
     # Conservative ties: codec consumption/arrival precedes DMA beats.
     self.fifo_counts['word_ticks']+=1
     if self.shift_started is not None:
      self.shift_finished+=1;self.fifo_counts['shift_words_completed' if self.shift_valid else 'invalid_shift_words_completed']+=1
     self.shift_started=self.next_word;self.shift_valid=self.tx_level>0
     if self.tx_level:self.tx_level-=1
     else:self.fifo_counts['TX_underflow']+=1;self.error_flags|=0x100
     if self.rx_level<15:self.rx_level+=1
     else:self.fifo_counts['RX_overflow']+=1;self.error_flags|=0x400
     self.min_tx=min(self.min_tx,self.tx_level);self.max_rx=max(self.max_rx,self.rx_level)
     self.fifo_counts['arrival_lateness_max_cycles']=max(self.fifo_counts['arrival_lateness_max_cycles'],self.clock.cycles-due)
     self.status_due=self.next_word+(self.bit_period if self.phase_mode=='first-bit' else 0)
     self.next_word+=self.word_period
     continue
    if status==due:
     self.fifo_counts['status_updates']+=1
     self.tx_flag=self.tx_level<=13;self.rx_flag=self.rx_level>=2
     self.status_flags=(1 if self.tx_flag else 0)|(4 if self.rx_flag else 0)|self.error_flags
     self.publish_status()
     self.status_due=None;self.request_levels(due)
     continue
    due,seq,state,op=heapq.heappop(self.events);kind,address,size,data=op
    assert self.owner==state['channel'].channel
    self.observe_payload(kind,state,due)
    if kind=='write':self.dma_span(address,size,True);self.m.uc.mem_write(address,data);value=None
    elif kind in ('rxread','rxskip'):value=None
    else:self.dma_span(address,size,False);value=bytes(self.m.uc.mem_read(address,size))
    self.payload_counts[kind+'_beats']+=1
    self.payload_counts['service_lateness_cycles_max']=max(self.payload_counts['service_lateness_cycles_max'],self.clock.cycles-due)
    self.advance(state,due,value)
    self.request_levels(due) # persistent level requests reassert after completion
   if self.owner is None:self.dispatch(self.clock.cycles)
  finally:self.servicing=False
 def report(self):
  r=super().report()
  r['FIFO']=dict(configuration=self.fifo_config,depth=15,watermarks=2,initial_TX_words=14,initial_RX_words=0,word_period=str(self.word_period),TX_level=self.tx_level,RX_level=self.rx_level,minimum_TX=self.min_tx,maximum_RX=self.max_rx,counts=dict(self.fifo_counts),limits=['Snapshot occupancy and serial phase supplied, not captured from hardware','Two serial words per assumed 48 kHz frame','FIFO occupancy modeled; actual codec signal and shift-register phase unverified','Basic-block CPU and assumed memory costs'])
  r['serial_phase']=dict(policy=self.phase_mode,bit_period=str(self.bit_period),status_due=str(self.status_due),shift_valid=self.shift_valid,shift_started=str(self.shift_started),status_reads=self.status_reads,status_writes=self.status_writes,status_flags=hex(self.status_flags),completed_words=self.shift_finished,error_flags=hex(self.error_flags),limits=['Word-validity model only, no bitwise codec waveform','Status assertion at first-bit completion; request acknowledged at minor acceptance and occupancy guarded on resubmission','Other SSI status bits and physical shift-register pipeline unverified'])
  r['audio_event_timing']['limits'].append('Next-frame counters inherited for diagnostics only; FIFO occupancy is the deadline criterion here')
  return r
