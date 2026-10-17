import pathlib
s=pathlib.Path('work/measure-cycle-audio-deadlines.py').read_text()
s=s.replace('from emu.cftiming import deadline_report,measured_period', '''from emu.cftiming import deadline_report,measured_period
from emu import edma_sw
from shared_memory_timing import MemoryTiming
original_bank=edma_sw.install_bank
def python_bank(m,ev,**kw):
 kw['native']=False
 return original_bank(m,ev,**kw)
edma_sw.install_bank=python_bank''')
s=s.replace("'zero wait, no cache misses or bus contention'", "'Cache maintenance and serialized DDR resource sensitivity; instant DMA payload copy with delayed DONE; no physical cache-value simulation'")
s=s.replace("m=session.m;uc=m.uc;m.ensure(RAM)", "m=session.m;uc=m.uc;m.ensure(RAM);session.memtime=MemoryTiming(session,fill=int(os.environ.get('MEM_FILL','20')),writeback=int(os.environ.get('MEM_WRITEBACK','16')),beat=int(os.environ.get('MEM_BEAT','4')),contention=os.environ.get('MEM_CONTENTION','1')=='1')")
s=s.replace("'icache':False", "'icache':True")
s=s.replace("ssi=session.ev['ssi0_dma'];sink=ssi.sink", "ssi=session.ev['ssi0_dma'];ssi.batch=False;sink=ssi.sink")
s=s.replace("session.run_ms(20)\n  if", "session.run_ms(20)\n  if")
s=s.replace("session.tap(session.code('PLAY'),hold_ms=20,after_ms=int(os.environ.get('DEADLINE_PLAY_MS','60')));session.tap(session.code('STOP'),hold_ms=20,after_ms=20)", '''session.press(session.code('PLAY'));session.run_ms(20);session.release(session.code('PLAY'))
  remaining=int(os.environ.get('DEADLINE_PLAY_MS','1000'))
  while remaining>0:
   chunk=min(50,remaining);session.run_ms(chunk);remaining-=chunk
   rec['progress_ms']=session.ms
   print(mode,'progress',round(session.ms,2),'ms',flush=True)
  session.tap(session.code('STOP'),hold_ms=20,after_ms=20)''')
s=s.replace("rec.update(clock=session.clock.report()", "rec.update(memory_model=session.memtime.report(),clock=session.clock.report()")
pathlib.Path('work/compare-shared-memory-runs.py').write_text(s)
