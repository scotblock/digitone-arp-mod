"""Observe DMA configuration and software-channel overlap; no firmware changes."""
import pathlib,json,collections,struct
exec(pathlib.Path('work/compare-timestamped-DMA-runs.py').read_text().split('\ndef run(mode):')[0])
from unicorn import UC_HOOK_MEM_WRITE
BaseMemory=MemoryTiming
class AuditMemory(BaseMemory):
 def install_dma(self):
  self.audit=collections.Counter();self.config_writes=[];self.starts=[];self.descriptors=[];self.boundaries=[]
  self.initial_config=self.configuration();super().install_dma()
  def cfg(uc,typ,address,size,value,d):
   if address<0xfc044004 or 0xfc044100<=address<0xfc044140:
    self.config_writes.append(dict(pc=hex(uc.reg_read(UC_M68K_REG_PC)),address=hex(address),size=size,value=hex(value)))
  self.hooks.append(self.m.uc.hook_add(UC_HOOK_MEM_WRITE,cfg,begin=0xfc044000,end=0xfc04413f))
  for ch in self.session.ev['edma_sw_bank'].channels.values():
   old=ch._transfer
   def start(uc,ensure=True,ch=ch,old=old):
    self.service_payload();others=sorted(self.active)
    self.audit['starts']+=1;self.audit['starts_with_other_software_active']+=bool(others)
    if len(self.starts)<24:self.starts.append(dict(channel=ch.channel,cycles=self.clock.cycles,others=others,CR=self.configuration()['CR']))
    return old(uc,ensure)
   ch._transfer=start
 def configuration(self):
  uc=self.m.uc
  return dict(CR=hex(struct.unpack('>I',uc.mem_read(0xfc044000,4))[0]),priority_bytes=bytes(uc.mem_read(0xfc044100,64)).hex())
 def walk(self,channel,tcd):
  # The parent mutates tcd only at final publish; descriptor read results become
  # the next TCD inside its generator, so observe them here on resumption.
  if len(self.descriptors)<24:self.descriptors.append(self.desc(channel.channel,tcd))
  gen=super().walk(channel,tcd);value=None
  while True:
   try:op=gen.send(value)
   except StopIteration:return
   value=yield op
   if op[0]=='descriptor':
    td=struct.unpack(edma_sw.TCD_FMT,value)
    if len(self.descriptors)<24:self.descriptors.append(self.desc(channel.channel,td))
    self.audit['scatter_descriptors']+=1
    self.audit['major_link_descriptors']+=bool(td[10]&32)
    self.audit['CITER_BITER_link_mismatch']+=bool((td[6]^td[9])&0x8000)
 def desc(self,ch,td):
  return dict(channel=ch,CITER=hex(td[6]),BITER=hex(td[9]),CSR=hex(td[10]),nbytes=td[3],count=edma_sw.iteration_count(td[6]),link=edma_sw.link_channel(td[6]))
 def advance(self,state,at,value=None):
  before=self.payload_counts['minor_loops_completed'];ch=state['channel'].channel
  others=[v for v in self.active if v!=ch]
  super().advance(state,at,value)
  if self.payload_counts['minor_loops_completed']!=before:
   self.audit['minor_boundaries']+=1;self.audit['minor_boundaries_with_competitor']+=bool(others)
   if others and len(self.boundaries)<24:self.boundaries.append(dict(channel=ch,others=others,cycles=at))
 def report(self):
  r=super().report();r['configuration_audit']=dict(initial=self.initial_config,final=self.configuration(),writes=self.config_writes,counts=dict(self.audit),starts=self.starts,descriptors=self.descriptors,contended_boundaries=self.boundaries)
  return r
MemoryTiming=AuditMemory
# Reuse the precise same stock workload and measurement machinery.
src=pathlib.Path('work/compare-timestamped-DMA-runs.py').read_text();exec(src[src.index('\ndef run(mode):'):])


