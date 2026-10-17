from pathlib import Path
s=Path('work/probe-PC-joined-UI-panel.py').read_text()
s=s.replace('for fake in [False,True]:',"for mode in ['LIVE','INITIALIZING','held_then_closed']:\n fake=False")
s=s.replace("r={'forced_semaphore_unblock':fake", "r={'mode':mode,'forced_semaphore_unblock':fake")
s=s.replace("'noteoff':0x400eae0c", "'noteoff':0x400eae0c,'internal_release':0x400eabb4")
s=s.replace("for key in ['KEYBOARD','T1','1','T2','5','PLAY','STOP']:", "for key in ['KEYBOARD','T1','1','T2']:")
anchor="  r.update(passed=s.halted is None,halted=s.halted)"
extra="""  r['panel_before_target']=panelin.state(s.m,s.profile)
  if mode=='INITIALIZING':s.m.uc.mem_write(0x47be2840,struct.pack('>I',0x494e4954))
  begin=len(r['events']);s.press(s.code('5'));s.run_ms(200);mark('target press',begin)
  if mode=='held_then_closed':s.m.uc.mem_write(0x47be2840,struct.pack('>I',0x494e4954))
  begin=len(r['events']);s.release(s.code('5'));s.run_ms(300);mark('target release',begin)
  r['closed_phase_is_host_fixture']=mode!='LIVE'
"""
assert anchor in s;s=s.replace(anchor,extra+anchor)
s=s.replace('Digitone-E04-PC-joined-UI-panel-probe.json','Digitone-E04-PC-joined-UI-panel-tests.json')
s=s.replace("print('PANEL',fake", "print('PANEL',mode")
exec(compile(s,'joined-UI-panel-controls','exec'))
