from pathlib import Path
s=Path('work/probe-PC-joined-UI-panel.py').read_text()
s=s.replace('for fake in [False,True]:',"for mode in ['LIVE','INITIALIZING','held_then_closed','two_held']:\n fake=False")
s=s.replace("r={'forced_semaphore_unblock':fake", "r={'mode':mode,'forced_semaphore_unblock':fake")
s=s.replace("'noteoff':0x400eae0c", "'noteoff':0x400eae0c,'internal_release':0x400eabb4")
s=s.replace("for key in ['KEYBOARD','T1','1','T2','5','PLAY','STOP']:","for key in ['KEYBOARD','T1','1','T2']:")
anchor="   points={'panel_IRQ'"
install="""   deferred_spec=json.loads(Path('work/os144/PC_ONLY-deferred-release-overlay.json').read_text());deferred_code=Path('work/os144/PC_ONLY-deferred-release-overlay.bin').read_bytes()
   s.m.load(deferred_code,deferred_spec['base']);s.m.install_isa_patches_scoped(deferred_code,deferred_spec['base']);s.m.ensure(deferred_spec['count']);s.m.uc.mem_write(deferred_spec['count'],bytes(deferred_spec['storage_bytes']))
   for h in deferred_spec['hooks']:
    assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['previous'];s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
"""
s=s.replace(anchor,install+anchor)
anchor="  r.update(passed=s.halted is None,halted=s.halted)"
extra="""  spec=json.loads(Path('work/os144/PC_ONLY-deferred-release-overlay.json').read_text());u=s.m.uc
  if mode=='INITIALIZING':u.mem_write(0x47be2840,struct.pack('>I',0x494e4954))
  begin=len(r['events']);s.press(s.code('5'));s.run_ms(200);mark('target press',begin)
  if mode=='two_held':s.press(s.code('6'));s.run_ms(150)
  if mode in ['held_then_closed','two_held']:u.mem_write(0x47be2840,struct.pack('>I',0x494e4954))
  begin=len(r['events']);s.release(s.code('5'));s.run_ms(200)
  if mode=='two_held':s.release(s.code('6'));s.run_ms(200)
  mark('target release',begin);r['pending_before_resume']=rd(u,spec['count'])
  if mode in ['held_then_closed','two_held','INITIALIZING']:
   r['retained_count_before_resume']=rd(u,0x41994e84)
   expected=2 if mode=='two_held' else 1
   assert rd(u,spec['count'])==expected and rd(u,0x41994e84)==(0 if mode=='INITIALIZING' else expected)
   # The closed transition is a declared phase fixture. Reopening uses the
   # actual patched completion helper, not a host LIVE write. Preserve paused
   # task registers and budget; guest release/phase/storage effects persist.
   ids=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC];saved={q:u.reg_read(q) for q in ids}
   u.mem_write(0x47fdff00,struct.pack('>II',0xdeadbee0,1));u.reg_write(UC_M68K_REG_SR,0x201f);u.reg_write(UC_M68K_REG_A7,0x47fdff00)
   budget=s.m._fast_stepper_obj;old=(budget.left,budget.blocks);budget.left=10000;begin=len(r['events']);u.emu_start(0x47fa0044,0xdeadbee0,count=100000);budget.left,budget.blocks=old
   assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and u.reg_read(UC_M68K_REG_D0)==1 and rd(u,0x47be2840)==0x4c495645 and rd(u,spec['count'])==0 and rd(u,spec['drain'])==0 and rd(u,0x41994e84)==0
   r['native_drain_events']=r['events'][begin:];r['retained_count_after_resume']=rd(u,0x41994e84)
   u.reg_write(UC_M68K_REG_SR,saved[UC_M68K_REG_SR])
   for q,v in saved.items():
    if q!=UC_M68K_REG_SR:u.reg_write(q,v)
   begin=len(r['events']);s.tap(s.code('7'),hold_ms=100,after_ms=300);mark('fresh panel note after native resume',begin)
   assert 'live_producer' in r['marks'][-1]['events'] and 'publish' in r['marks'][-1]['events'] and rd(u,0x41994e84)==0
  r['closed_phase_is_host_fixture']=mode!='LIVE'
"""
s=s.replace(anchor,extra+anchor).replace('Digitone-E04-PC-joined-UI-panel-probe.json','Digitone-E04-PC-deferred-release-panel.json').replace("print('PANEL',fake", "print('DEFERRED PANEL',mode")
exec(compile(s,'deferred-release-panel','exec'))
