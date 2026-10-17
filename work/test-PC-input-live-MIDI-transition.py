"""Actual receiver input on a retained INITIALIZING checkpoint, then native LIVE."""
from pathlib import Path
exec(Path('work/probe-PC-startup-settled-MIDI.py').read_text().split('\nfor c in startup')[0])
input_cfg=json.loads(Path('work/os144/PC_ONLY-input-live-overlay.json').read_text());input_blob=Path('work/os144/PC_ONLY-input-live-overlay.bin').read_bytes()
c=next(x for x in startup['cases'] if x['image']=='E04_restored');root=Path(c['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env());s=None
r={'PC_only':True,'events':[],'initial_phase_from_actual_prior_startup':True,'host_phase_writes':False,'failure':None}
try:
 def install(s):
  for base,length in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280)]:s.m.install_isa_patches_scoped(bytes(s.m.uc.mem_read(base,length)),base)
  s.m.load(input_blob,input_cfg['base']);s.m.install_isa_patches_scoped(input_blob,input_cfg['base'])
  for h in input_cfg['hooks']:
   assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'];s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
  def event(u,pc,n,d):r['events'].append({'pc':hex(pc),'phase':hex(rd(u,0x47be2840)),'ms':s.now_ms()})
  for pc in [0x400025c8,0x400e842c,0x400eb2d2,0x400eb166,0x400eae5c,0x400eaf48,0x40100252]:s.at(pc,event)
 s=Session(c['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);s.run_ms(100);u=s.m.uc
 assert rd(u,0x47be2840)==0x494e4954 and rd(u,0x41368d64)==3 and rd(u,0x41368d88)==1
 mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,);channel=rd(u,0x41368d2c)&15
 def send(data):
  for i,b in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,b)
  mi.received+=len(data);s.run_ms(300)
 start=len(r['events']);send([0x90|channel,64,100]);closed=r['events'][start:]
 assert any(e['pc']=='0x400eb2d2' for e in closed) and not any(e['pc'] in ['0x400eb166','0x400eae5c','0x40100252'] for e in closed)
 assert rd(u,0x47be2840)==0x494e4954
 r['closed_input_native_rejected_before_cached_and_live_routes']=True
 # Paused functional control: full stock startup already completed. Its old
 # overlay never published LIVE. Use the native phase helper with explicit
 # success argument, rather than replay the cold bootstrap checks in live UI.
 # The new bootstrap completion conditions are tested by continuous runs.
 rr=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC];saved={q:u.reg_read(q) for q in rr}
 phase_cfg=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text())
 s.m.ensure(0x47fdff00);u.mem_write(0x47fdff00,struct.pack('>II',0xdeadbee0,1));u.reg_write(UC_M68K_REG_SR,0x201f);u.reg_write(UC_M68K_REG_A7,0x47fdff00)
 budget=getattr(s.m,'_fast_stepper_obj');old_budget=(budget.left,budget.blocks);budget.left=1000
 u.emu_start(phase_cfg['layout']['complete']['address'],0xdeadbee0,count=2000)
 budget.left,budget.blocks=old_budget
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and rd(u,0x47be2840)==0x4c495645
 r['transition_helper_success_argument_fixture']=1
 u.reg_write(UC_M68K_REG_SR,saved[UC_M68K_REG_SR])
 for q,v in saved.items():
  if q!=UC_M68K_REG_SR:u.reg_write(q,v)
 start=len(r['events']);send([0x90|channel,65,100]);opened=r['events'][start:]
 assert any(e['pc']=='0x400eb166' for e in opened) and any(e['pc']=='0x400eae5c' for e in opened) and any(e['pc']=='0x40100252' for e in opened)
 assert all(e['phase']=='0x4c495645' for e in opened)
 send([0x80|channel,65,0]);r.update(passed=True,native_completion_publishes_LIVE=True,open_input_reaches_cached_selector_live_producer_and_queue=True,delivered=mi.delivered,received=mi.received,halted=s.halted)
 assert mi.delivered==mi.received and s.halted is None
except Exception:r['failure']=traceback.format_exc();r['passed']=False
finally:
 if s:s.close()
r['limits']=['Receiver/session is paused for a native phase-helper call with explicit success argument 1; task CPU and stepper counters are restored afterward. This is a functional handoff, not naturally scheduled boot concurrency or a cold completion replay.','Phase and stock gate values are inherited; no host phase write is used to open LIVE.','New bootstrap completion conditions and full original final call are tested by the three separate continuous startup runs.','No USB, sustained-note/panel bypass, hardware DMA latching or physical timing certification.']
Path('outputs/Digitone-E04-PC-input-live-MIDI-transition.json').write_text(json.dumps(r,indent=2));print('MIDI transition',r['passed'],flush=True)
if not r['passed']:raise SystemExit(1)
