from pathlib import Path
exec(Path('work/probe-PC-startup-settled-MIDI.py').read_text().split('\nfor c in startup')[0])
from emu import panelin
startup_ui=json.loads(Path('outputs/Digitone-E04-PC-release-reset-startup-startup.json').read_text());c=next(x for x in startup_ui['cases'] if x['image']=='E04_restored');root=Path(c['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
ui_cfg=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text());site_map=json.loads(Path('work/os144/stock-probe-map.json').read_text());rows=[]
for fake in [False,True]:
 longrun.build=baseline_build if fake else build_without_forced_unblock
 r={'forced_semaphore_unblock':fake,'events':[],'marks':[]};rows.append(r);s=None
 try:
  def install(s):
   for base,n in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280),(0x47fa0600,492),(0x47fa0900,594)]:s.m.install_isa_patches_scoped(bytes(s.m.uc.mem_read(base,n)),base)
   for h in ui_cfg['hooks']:
    assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'];s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
   points={'panel_IRQ':rd(s.m.uc,0x40000268),'panel_rx':rd(s.m.uc,s.profile.uart8_rx_callback),'queue_send':s.profile.queue_send,'ui_key_dispatch':s.profile.ui_key_dispatch,'packet':0x400eb2d2,'selector':0x400eb166,'live_producer':0x400eae5c,'noteoff':0x400eae0c,'sustain_release':0x400f0580,'release_decision':0x400eabdc,'publish':0x40100252}
   for key in ['producer','pitch']:points[key]=int(site_map['sites'][key]['new'],16)
   r['sites']={k:hex(v) if v else None for k,v in points.items()}
   for label,pc in points.items():
    if pc:
     def observe(u,pc,n,d,label=label):
      if len(r['events'])<1500:r['events'].append({'kind':label,'pc':hex(pc),'phase':hex(rd(u,0x47be2840)),'ms':s.now_ms(),'D0':hex(u.reg_read(UC_M68K_REG_D0))})
     s.at(pc,observe)
  s=Session(c['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);s.run_ms(200)
  def mark(label,begin):r['marks'].append({'label':label,'events':[e['kind'] for e in r['events'][begin:]],'panel':panelin.state(s.m,s.profile),'frames':len(s.frames),'note_counts':[rd(s.m.uc,0x41994e80+i*4) for i in range(8)]})
  for key in ['KEYBOARD','T1','1','T2','5','PLAY','STOP']:
   begin=len(r['events']);s.tap(s.code(key),hold_ms=100,after_ms=300);mark(key,begin)
  r.update(passed=s.halted is None,halted=s.halted)
 except Exception:r.update(passed=False,failure=traceback.format_exc())
 finally:
  if s:s.close()
 print('PANEL',fake,r.get('passed'),flush=True)
Path('outputs/Digitone-E04-PC-joined-UI-panel-probe.json').write_text(json.dumps({'PC_only':True,'cases':rows,'limits':['Forced unblock case is an explicit model workaround and is not naturally scheduled panel proof.','Native seeded UI/page state and peripheral shortcuts remain; code is host-loaded.']},indent=2))

