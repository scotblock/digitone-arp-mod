"""Native stopped preparation, then uninterrupted cycle-aware handoff."""
import pathlib,os
source=pathlib.Path('work/test-cache-startup-handoff.py').read_text()
source=source.replace("OUT=pathlib.Path('outputs/Digitone-cache-startup-handoff'", "OUT=pathlib.Path('outputs/Digitone-cycle-complete-handoff'")
source=source.replace('session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=install)', 'session=Session(paths.gui,syx=str(SYX),ddr=DDR,hle=False,on_machine=install)')
source=source.replace('from emu import midi', '''from emu import midi,edma_sw
original_bank=edma_sw.install_bank
def python_bank(m,ev,**kw):
 kw['native']=False
 return original_bank(m,ev,**kw)
edma_sw.install_bank=python_bank
from emu.cftiming import CycleClock,CycleStepper,deadline_report,measured_period
from emu import longrun
from phase_audio_dma import PhaseAudioMemory
''')
insert='''
def enable_timing(s):
 # All copy/paste and stopped pattern selection already executed natively.
 # Switch before PLAY; no guest snapshot, helper, queue, or pattern replay.
 idle=set(longrun.db.find_idle_spins(s.main_img,longrun.db.MAIN_LOAD))
 s.clock=CycleClock(s.m,idle=idle,fsys=264000000,accel='max',stalls=True,icache=True)
 s.stepper=CycleStepper(s.clock);old_ips=s.ips;s.ips=s.clock.fsys
 for component in s.pits.sources:
  prior_bus=getattr(component,'fbus',32000000)
  ratio=s.ips/component.ips*prior_bus/(s.ips/2)
  component.fbus=s.ips/2
  component.next=[None if n is None else component.now+(n-component.now)*ratio for n in component.next]
  component.__dict__.pop('_period_cache',None);component.ips=s.ips
 for peer in s.sources:
  if hasattr(peer,'ips'):peer.ips=s.ips
 s.ev['ssi0_dma'].align(s.pits.now)
 s._t0=s.pits.now;s.ms=0;s.pits._cycle_epoch=s._t0-s.clock.cycles
 s.memtime=PhaseAudioMemory(s,fill=int(os.environ.get('MEM_FILL','40')),writeback=int(os.environ.get('MEM_WRITEBACK','32')),beat=int(os.environ.get('MEM_BEAT','8')),contention=True)
 result['timing_start']={'before_transport_start':True,'native_preparation_complete':True,'core_hz_candidate':s.ips,'bus_hz_candidate':s.ips//2,'hle':False,'limits':['Uncalibrated instruction/cache/DDR costs','FIFO/serial phase remains a model fixture','Prepared stopped state was executed without cycle costs']}
 result['DMA_captures']=[]
 stores={};last_capture={};ssi=s.ev['ssi0_dma'];sink=ssi.sink
 def stored(uc,access,a,n,value,d):
  for word in range(a,a+n,4):stores[word]=s.clock.cycles
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,stored,begin=0x80001000,end=0x80002fff)
 def captured(raw):
  end=ssi._u32(ssi.p.tx_chan,0);start=end-len(raw);prior=last_capture.get(end-4,-1)
  obs=[stores.get(w) for w in range(start,end,4)]
  fresh=all(t is not None and t>prior for t in obs)
  margin=s.clock.cycles-max(obs) if all(t is not None for t in obs) else None
  result['DMA_captures'].append({'cycles':s.clock.cycles,'ms':s.now_ms(),'start':hex(start),'bytes':len(raw),'all_words_fresh':fresh,'completion_margin_cycles':margin})
  last_capture[end-4]=s.clock.cycles;sink(raw)
 ssi.sink=captured
 for name in ['cache_builds','cache_copies','events','quantizer_calls','pitch_outputs']:
  result[name]=[]
 result['marks']=[]

'''
source=source.replace('def send_midi(data):',insert+'def send_midi(data):')
source=source.replace(" mi.attach(session.m,session.ips);", " enable_timing(session)\n mi.attach(session.m,session.ips);")
# Capture cycles alongside existing event/generation/ownership witnesses.
source=source.replace("'ms':s.now_ms(),", "'cycles':s.clock.cycles if s.clock else None,'ms':s.now_ms(),")
source=source.replace("'ms':session.now_ms(),", "'cycles':session.clock.cycles if session.clock else None,'ms':session.now_ms(),")
# Stop once fresh receiving notes and the delayed original have both run;
# the native handoff itself is never shortened or simulated by pointer writes.
source=source.replace(" session.run_ms(2000);mark('queued note observation after handoff');", " session.run_ms(700);mark('queued note observation after handoff');")
source=source.replace("result['firmware_sha256']=", """result['timing']={'clock':session.clock.report(),'memory':session.memtime.report(),'render_deadline':deadline_report(session.clock,191,176000),'measured_period':measured_period(session.clock,191)}
 result['firmware_sha256']=""")
source=source.replace(" if session:session.close()", " if session:\n  if session.clock:result['final_timing']={'clock':session.clock.report(),'memory':session.memtime.report(),'ms':session.now_ms()}\n  session.close()")
source=source.replace('Untimed native run; MIDI bytes', 'Cycle-aware PLAY through completed handoff; MIDI bytes')
exec(compile(source,'cycle-complete-handoff','exec'))
