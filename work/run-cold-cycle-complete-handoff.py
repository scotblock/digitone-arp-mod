"""Restore native stopped preparation into the standard timed Session path."""
import pathlib
outer=pathlib.Path('work/run-cycle-complete-handoff.py').read_text().split("exec(compile(source,'cycle-complete-handoff','exec'))")[0]
exec(compile(outer,'prepare-handoff-source','exec'))
a=source.index(' idle=set(longrun.db.find_idle_spins');b=source.index(" result['timing_start']=",a)
source=source[:a]+''' from emu import snapshot
 checkpoint=pathlib.Path('work/cache-native-prepared-handoff.snap')
 s.ev['checkpoint_components']['timers']=s.pits
 checkpoint_info=snapshot.save(s.m,str(checkpoint),s.st,components=s.ev['checkpoint_components'],manifest=s.ev['checkpoint_manifest'])
 result['prepared_checkpoint']={'path':str(checkpoint),'sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'native_copy_paste_completed':True,'transport_stopped':True,'info':checkpoint_info}
 s.close()
 def timed_install(timed):
  install(timed)
  timed.memtime=PhaseAudioMemory(timed,fill=int(os.environ.get('MEM_FILL','40')),writeback=int(os.environ.get('MEM_WRITEBACK','32')),beat=int(os.environ.get('MEM_BEAT','8')),contention=True)
 s=Session(str(checkpoint),syx=str(SYX),ddr=DDR,hle=False,timing={'fsys':264000000,'accel':'max','stalls':True,'icache':True},on_machine=timed_install)
''' +source[b:]
source=source.replace(" result['marks']=[]\n\ndef send_midi", " result['marks']=[]\n return s\n\ndef send_midi")
source=source.replace(' enable_timing(session)\n', ' session=enable_timing(session)\n')
source=source.replace(" # All copy/paste and stopped pattern selection already executed natively.\n # Switch before PLAY; no guest snapshot, helper, queue, or pattern replay.", " # Save native preparation and restore through the standard timed Session.\n # No helper or event/context metadata is reinstalled.")
# A coarse progress log confirms the clock advances, without changing state.
source=source.replace(" result['marks']=[]\n return s", """ result['marks']=[]
 import threading,time
 def heartbeat():
  while not result.get('_finished'):
   time.sleep(30)
   if not result.get('_finished'):print('timed progress',round(s.now_ms(),3),'cycles',s.clock.cycles,'instructions',s.clock.instructions,flush=True)
 threading.Thread(target=heartbeat,daemon=True).start()
 return s""")
source=source.replace('finally:\n if session:', "finally:\n result['_finished']=True\n if session:")
exec(compile(source,'cold-cycle-complete-handoff','exec'))
