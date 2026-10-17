import pathlib
s=pathlib.Path('work/measure-cycle-audio-deadlines.py').read_text()
s=s.replace("from emu.cftiming import deadline_report,measured_period",'''from emu.cftiming import deadline_report,measured_period
import emu.cftiming as timing
class RoundRobinCache:
 def __init__(self):
  self.tags=[[None]*4 for _ in range(128)];self.next=[0]*128;self.hits=self.misses=0
 def touch(self,addr,size):
  if not 0x40000000<=addr<0x48000000:return 0
  misses=0
  for line in range(addr//16,(addr+size-1)//16+1):
   index=line%128;row=self.tags[index]
   if line in row:self.hits+=1
   else:
    slot=row.index(None) if None in row else self.next[index]
    row[slot]=line;self.next[index]=(slot+1)%4;self.misses+=1;misses+=1
  return misses
timing.ICache=RoundRobinCache
PENALTY=int(os.environ.get('DEADLINE_MISS_PENALTY','20'))''')
s=s.replace("'icache':False", "'icache':True,'miss_penalty':PENALTY")
s=s.replace("'zero wait, no cache misses or bus contention'", "'Instruction-cache round-robin sensitivity only; no data-cache timing, DDR contention or store-buffer timing'")
s=s.replace("m=session.m;uc=m.uc;m.ensure(RAM)","m=session.m;uc=m.uc;m.ensure(RAM);rec['initial_control_registers']={hex(k):hex(v) for k,v in m.ctlregs.items()}")
pathlib.Path('work/measure-cache-sensitivity.py').write_text(s)
