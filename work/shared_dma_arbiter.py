"""PC-only shared eDMA arbiter: software self-links and SSI minor requests."""
import collections,heapq,struct,zlib
from types import SimpleNamespace
from timestamped_dma import TimestampedMemory
from emu import edma_sw as e

class SharedDmaMemory(TimestampedMemory):
 supports_restart_latching=True
 def install_dma(self):
  self.batching_audio=False;self.owner=None;self.pending={};self.last_group=0;self.last_channel={g:0 for g in range(4)}
  self.arbitration=collections.Counter();self.grants=[]
  uc=self.m.uc;old=int.from_bytes(uc.mem_read(0xfc044000,4),'big')
  self.configuration_repair={'original_CR':hex(old),'documented_reset_fields_seeded':not bool(old&0xff00)}
  if not old&0xff00:
   uc.mem_write(0xfc044000,(old|0xe400).to_bytes(4,'big'));uc.mem_write(0xfc044100,bytes(range(64)))
  super().install_dma()
  for ch in self.session.ev['edma_sw_bank'].channels.values():
   def apply(ch=ch):
    self.service_payload()
    if ch.channel in self.active:
     self.counts['DMA_completion_polls_deferred']+=1
     csr=ch._u16(e.CSR)&~(e.CSR_DONE|e.CSR_ACTIVE|e.CSR_START)
     state=self.active[ch.channel]
     ch._w16(e.CSR,csr|(e.CSR_ACTIVE if self.owner==ch.channel else e.CSR_START)|(e.CSR_START if state.get('restart_latched') else 0));return False
    if ch._pending is not None:ch._w16(e.CSR,ch._pending);ch._pending=None;return True
    return False
   ch._apply=apply
  self.ssi=self.session.ev.get('ssi0_dma')
  if self.ssi:
   self.ssi.batch=False
   def minors(channel,capture,n):
    for _ in range(n):self.request_ssi(channel,capture)
   self.ssi._run_minors=minors
   original_service=self.ssi.service
   def service(done):
    self.batching_audio=True
    try:original_service(done)
    finally:self.batching_audio=False
    self.dispatch(self.clock.cycles)
   self.ssi.service=service

 def cr(self):return int.from_bytes(self.m.uc.mem_read(0xfc044000,4),'big')
 def choose(self):
  cr=self.cr()
  if cr&0x20:return None
  if cr&0x80:raise RuntimeError('Shared arbiter: EMLM mode not implemented')
  groups={ch//16 for ch in self.pending}
  if not groups:return None
  if cr&8:g=min(groups,key=lambda g:(self.last_group-g-1)%4)
  else:
   pri=[(cr>>(8+2*g))&3 for g in range(4)]
   if len(set(pri))!=4:raise RuntimeError('Duplicate fixed group priorities')
   g=max(groups,key=lambda g:pri[g])
  candidates=[ch for ch in self.pending if ch//16==g]
  if cr&4:ch=min(candidates,key=lambda ch:(self.last_channel[g]-ch%16-1)%16)
  else:
   priorities=bytes(self.m.uc.mem_read(0xfc044100+g*16,16))
   if len({v&15 for v in priorities})!=16:raise RuntimeError('Duplicate fixed channel priorities')
   if any(v&0x80 for v in priorities):raise RuntimeError('DMA preemption not implemented')
   ch=max(candidates,key=lambda ch:priorities[ch%16]&15)
  self.last_group=g;self.last_channel[g]=ch%16
  return ch

 def dispatch(self,at,preferred=None):
  if self.owner is not None or self.batching_audio:return
  ch=preferred if preferred in self.pending else self.choose()
  if ch is None:return
  state,op=self.pending.pop(ch);self.owner=ch
  # The sole software START latch is consumed when a minor wins service.
  state['restart_latched']=False
  self.arbitration['grants']+=1;self.arbitration['audio_grants' if state.get('ssi') else 'software_grants']+=1
  self.arbitration['grants_with_competitors']+=bool(self.pending)
  if len(self.grants)<32:self.grants.append(dict(channel=ch,cycles=at,waiting=sorted(self.pending)))
  if state.get('ssi'):
   self.ssi._w16(ch,e.CSR,(self.ssi._u16(ch,e.CSR)&~(e.CSR_DONE|e.CSR_START))|e.CSR_ACTIVE)
  else:
   c=state['channel'];c._w16(e.CSR,(c._u16(e.CSR)&~(e.CSR_DONE|e.CSR_START))|e.CSR_ACTIVE)
  if op[0]=="activate":op=next(state["generator"])
  self.schedule(state,op,at)

 def schedule(self,state,op,at):
  kind,address,size,data=op;cost=((size+3)//4)*self.beat
  due=self.bus.reserve(at,cost,'DMA_DDR') if self.contention and 0x40000000<=address<0x80000000 else at+cost
  self.sequence+=1;heapq.heappush(self.events,(due,self.sequence,state,op))

 def advance(self,state,at,value=None):
  ch=state['channel'].channel
  try:op=state['generator'].send(value)
  except StopIteration:
   self.active.pop(ch,None);self.owner=None;self.dma_ready[ch]=at
   self.payload_counts['major_transfers_completed' if not state.get('ssi') else 'audio_minor_completed']+=1
   if not state.get('ssi'):
    c=state['channel'];c._apply()
    if state.get('restart_latched'):
     self.payload_counts['software_requests_surviving_major_completion']+=1
     c._transfer(self.m.uc,False)
   self.dispatch(at);return
  if op[0] in ('boundary','activate'):
   if op[0]=='boundary':self.arbitration['self_link_boundaries']+=1
   if state.get('ssi'):raise RuntimeError('Unexpected SSI self-link')
   continuous=bool(op[1] and self.cr()&64)
   if op[0]=='boundary':self.owner=None
   self.pending[ch]=(state,('activate',False,0,None))
   c=state['channel'];c._w16(e.CSR,(c._u16(e.CSR)&~e.CSR_ACTIVE)|e.CSR_START)
   self.arbitration['continuous_self_restarts']+=continuous
   self.dispatch(at,ch if continuous else None)
  elif self.owner==ch:self.schedule(state,op,at)
  else:
   self.pending[ch]=(state,op)
   if not state.get('ssi'):
    c=state['channel'];c._w16(e.CSR,(c._u16(e.CSR)&~e.CSR_ACTIVE)|e.CSR_START)
   self.dispatch(at)

 def request_ssi(self,ch,capture):
  if ch not in self.ssi.enabled:return
  self.service_payload();self.arbitration['audio_requests']+=1
  if ch in self.active:
   self.arbitration['audio_requests_dropped_while_pending']+=1;return
  state={'channel':SimpleNamespace(channel=ch),'ssi':True,'generator':self.audio_minor(ch,capture)}
  self.active[ch]=state;self.advance(state,self.clock.cycles)

 def audio_minor(self,ch,capture):
  s=self.ssi;td=list(struct.unpack(e.TCD_FMT,self.m.uc.mem_read(s._tcd(ch),32)))
  src,attr,soff,nbytes,slast,dst,citer,doff,dlast,biter,csr=td
  if citer&0x8000 or biter&0x8000 or attr&0x707!=0x202 or not nbytes or nbytes%4:raise RuntimeError('Unsupported shared SSI descriptor')
  if not citer:return
  supplied=bytes(s.rx_source(nbytes) or b'') if not capture and s.rx_source else b''
  if supplied and len(supplied)!=nbytes:raise RuntimeError('SSI RX supplied size mismatch')
  data=bytearray()
  for beat in range(nbytes//4):
   if capture:data.extend((yield ('read',src,4,None)))
   else:
    # Preserve upstream's unknown external RX signal instead of inventing it.
    yield ('rxread',src,4,None)
    chunk=supplied[beat*4:beat*4+4] if supplied else None
    data.extend(chunk if chunk else bytes(4))
   src=e.modulo_add(src,soff,attr>>11)
  for beat in range(nbytes//4):
   if capture:yield ('write',dst,4,bytes(data[beat*4:beat*4+4]))
   elif supplied:yield ('write',dst,4,bytes(data[beat*4:beat*4+4]))
   else:yield ('rxskip',dst,4,None)
   dst=e.modulo_add(dst,doff,(attr>>3)&31)
  s._w32(ch,e.SADDR,src);s._w32(ch,e.DADDR,dst);s._w16(ch,e.CITER,citer-1)
  if capture:
   s.tx_bytes+=len(data);s.tx_crc32=zlib.crc32(data,s.tx_crc32)
   if s.sink:s.sink(bytes(data))
  elif supplied:s.rx_bytes+=len(supplied)
  if citer==1:s._complete_major(ch,src,dst,biter)
  elif capture and csr&4 and citer-1==(biter&0x7fff)//2:
   s.half_loops+=1;s.int50_asserted=True;s.int50_delivered=False
  s._w16(ch,e.CSR,(s._u16(ch,e.CSR)&~(e.CSR_ACTIVE|e.CSR_START|e.CSR_DONE))|(e.CSR_DONE if citer==1 else 0))

 def service_payload(self):
  if self.servicing:return
  self.servicing=True
  try:
   while self.events and self.events[0][0]<=self.clock.cycles:
    due,seq,state,op=heapq.heappop(self.events);kind,address,size,data=op
    if self.owner!=state['channel'].channel:raise RuntimeError('DMA event without controller ownership')
    if kind=='write':self.dma_span(address,size,True);self.m.uc.mem_write(address,data);value=None
    elif kind in ('rxread','rxskip'):value=None
    else:self.dma_span(address,size,False);value=bytes(self.m.uc.mem_read(address,size))
    self.payload_counts[kind+'_beats']+=1
    self.payload_counts['service_lateness_cycles_max']=max(self.payload_counts['service_lateness_cycles_max'],self.clock.cycles-due)
    if len(self.payload_samples)<32:self.payload_samples.append(dict(channel=state['channel'].channel,kind=kind,address=hex(address),size=size,due=due,observed=self.clock.cycles))
    self.advance(state,due,value)
   if self.owner is None:self.dispatch(self.clock.cycles)
  finally:self.servicing=False

 def report(self):
  r=super().report();r['shared_arbiter']=dict(configuration=self.configuration_repair,CR=hex(self.cr()),counts=dict(self.arbitration),grants=self.grants,owner=self.owner,pending=sorted(self.pending),limits=['Other peripheral DMA paths are not routed here','Unknown RX data preserved','SSI scatter/gather descriptor fetch still delegated to baseline','Request arrival and interrupt delivery remain outer-scheduler granular','No calibrated arbitration-cycle overhead'])
  return r
 def walk(self,channel,tcd):
     # Requests (including self-links) activate one minor each. Sample the
     # local-memory descriptor when arbitration grants that minor, then
     # retain its internal addresses until the minor's writeback.
     seen=set();minor=0;depth=0
     yield ('activate',False,0,None)
     while depth < e.MAX_LINKS:
         tcd=list(struct.unpack(e.TCD_FMT,self.m.uc.mem_read(channel.tcd,32)))
         src,attr,soff,nbytes,slast,dst,citer_raw,doff,dlast,biter,csr=tcd
         if csr&32:raise RuntimeError('Software major channel links not implemented')
         if bool(citer_raw&0x8000)!=bool(biter&0x8000):raise RuntimeError('CITER/BITER link mismatch')
         count=e.iteration_count(citer_raw)
         ss,ds=1<<((attr>>8)&7),1<<(attr&7)
         smod,dmod=attr>>11,(attr>>3)&31
         if not count or not nbytes or nbytes%ss or nbytes%ds or count*nbytes>e.MAX_BYTES:
             raise RuntimeError('Unsupported or invalid timestamped DMA descriptor')
         if count > 1 and e.link_channel(citer_raw) != channel.channel:
             raise RuntimeError('Shared arbiter requires observed self-linked software descriptors')
         buffer=bytearray()
         for beat in range(nbytes//ss):
             value=yield ('read',src,ss,None)
             buffer.extend(value);src=e.modulo_add(src,soff,smod)
         for beat in range(nbytes//ds):
             yield ('write',dst,ds,bytes(buffer[beat*ds:(beat+1)*ds]))
             dst=e.modulo_add(dst,doff,dmod)
         self.payload_counts['minor_loops_completed']+=1
         channel.bytes_moved+=nbytes;self.channels[channel.channel]+=nbytes
         channel._w32(e.SADDR,src);channel._w32(e.DADDR,dst)
         channel._w16(e.CITER,(citer_raw&0xfe00 if citer_raw&0x8000 else 0)|(count-1))
         minor+=1
         if count>1:
             yield ('boundary',True,0,None)
             continue
         # Dynamic CSR flags are sampled at retirement. BITER can have been
         # changed by the guest; SADDR/DADDR/CITER writes lose to writeback.
         final=list(struct.unpack(e.TCD_FMT,self.m.uc.mem_read(channel.tcd,32)))
         csr=final[10];src=(src+e._signed(slast,32))&0xffffffff
         final[0]=src;final[5]=dst;final[6]=final[9]
         if not csr&e.CSR_ESG:
             final[5]=(dst+e._signed(dlast,32))&0xffffffff
             self.m.uc.mem_write(channel.tcd,struct.pack(e.TCD_FMT,*final))
             channel._pending=(csr&~(e.CSR_START|e.CSR_ACTIVE))|e.CSR_DONE
             channel.transfers+=1
             return
         if dlast in seen or dlast%32:raise RuntimeError('Invalid timestamped scatter-gather chain')
         seen.add(dlast)
         descriptor=yield ('descriptor',dlast,32,None)
         self.m.uc.mem_write(channel.tcd,descriptor)
         channel.links_followed+=1;depth+=1
         yield ('boundary',False,0,None)
     raise RuntimeError('Timestamped scatter-gather chain exceeded bound')
