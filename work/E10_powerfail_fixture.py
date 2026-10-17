"""Narrow PC-only W1C adapter for eSDHC CC/TC used by stock shutdown.
Reference: MCF54418RM rev 5, section 25.3.10 / table 25-14 (IRQSTAT).
Controller-generated bits still come from Esdhc; this creates no completion.
"""
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from emu.esdhc import BASE,IRQSTAT
class PolledCompletionStatus:
 def __init__(self,es):
  self.es=es;self.uc=es.uc;self.value=es._get(IRQSTAT);self.acks=[]
  self.original_get=es._get;self.original_put=es._put
  def get(off):return self.value if off==IRQSTAT else self.original_get(off)
  def put(off,value):
   if off==IRQSTAT:self.value=value&0xffffffff
   self.original_put(off,value)
  es._get=get;es._put=put
  self.uc.hook_add(UC_HOOK_MEM_WRITE,self.written,begin=BASE+IRQSTAT,end=BASE+IRQSTAT+3)
  self.uc.hook_add(UC_HOOK_MEM_READ,self.read,begin=BASE+IRQSTAT,end=BASE+IRQSTAT+3)
 def written(self,u,access,a,n,value,d):
  shift=(4-(a-(BASE+IRQSTAT))-n)*8
  mask=(value&((1<<(n*8))-1))<<shift
  before=self.value
  # Only CC and TC require corrected behavior in this scoped adapter.
  corrected=(before&~mask)&3
  self.value=(before&~3)|corrected
  if len(self.acks)<300:self.acks.append(dict(before=before,write=mask,after=self.value))
 def read(self,u,access,a,n,value,d):
  u.mem_write(BASE+IRQSTAT,self.value.to_bytes(4,'big'))
