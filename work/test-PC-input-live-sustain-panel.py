"""Bounded session coverage; closed phase is an explicit negative-control fixture."""
from pathlib import Path
exec(Path('work/probe-PC-startup-settled-MIDI.py').read_text().split('\nfor c in startup')[0])
from unicorn import UC_HOOK_MEM_WRITE
import hashlib
startup_new=json.loads(Path('outputs/Digitone-E04-PC-input-live-startup-startup.json').read_text())
case=next(c for c in startup_new['cases'] if c['image']=='E04_restored')
input_manifest=json.loads(Path('work/os144/PC_ONLY-input-live-overlay.json').read_text())
site_map=json.loads(Path('work/os144/stock-probe-map.json').read_text())
sites={k:int(v['new'],16) for k,v in site_map['sites'].items()}
root=Path(case['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
report={'PC_only':True,'firmware_modified':False,'cases':[],'limits':['Closed session phase is supplied by host as a negative control, not reached by a proved stock warm transition.','Panel inputs and paced DIN execute actual recovered guest handlers, with existing emulator device/storage shortcuts.','Finite functional coverage does not certify concurrency, USB or physical cache/timing.']}
for mode in ['LIVE_guarded','LIVE_stock_entries','INITIALIZING_guarded','LIVE_held_then_closed']:
 r={'mode':mode,'events':[],'marks':[],'failure':None};report['cases'].append(r);s=None
 try:
  def install(s):
   for base,length in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280),(0x47fa0600,492)]:s.m.install_isa_patches_scoped(bytes(s.m.uc.mem_read(base,length)),base)
   if mode=='LIVE_stock_entries':
    for h in input_manifest['hooks'][:3]:s.m.uc.mem_write(h['site'],bytes.fromhex(h['stock']))
   points={'packet':0x400eb2d2,'selector':0x400eb166,'producer':0x400eae5c,'note_off':0x400eae0c,'publish':0x40100252}
   points.update({k:sites[k] for k in ['cc_handler','sustain_on','sustain_release']})
   for label,pc in points.items():
    s.at(pc,lambda u,pc,n,d,label=label:r['events'].append({'kind':label,'phase':hex(rd(u,0x47be2840)),'ms':s.now_ms()}))
  s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);s.run_ms(100);u=s.m.uc
  assert rd(u,0x47be2840)==0x4c495645 and rd(u,0x41368d64)==3
  if mode=='INITIALIZING_guarded':u.mem_write(0x47be2840,struct.pack('>I',0x494e4954))
  mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources+=(mi,);ch=rd(u,0x41368d2c)&15
  def mark(label,start):
   r['marks'].append({'label':label,'events':[e['kind'] for e in r['events'][start:]],'flags':bytes(u.mem_read(0x419afff4,8)).hex(),'lists':[hex(rd(u,0x419afffc+i*8)) for i in range(8)],'phase':hex(rd(u,0x47be2840))})
  def send(data,label):
   start=len(r['events'])
   for i,b in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,b)
   mi.received+=len(data);s.run_ms(120);mark(label,start)
  send([0xb0|ch,64,127],'sustain on')
  send([0x90|ch,60,100],'note on')
  send([0x80|ch,60,0],'explicit note off held')
  send([0x90|ch,60,0],'velocity zero note off held')
  if mode=='LIVE_held_then_closed':u.mem_write(0x47be2840,struct.pack('>I',0x494e4954))
  send([0xb0|ch,64,0],'sustain release')
  s.tap(s.code('KEYBOARD'),hold_ms=50,after_ms=150)
  for track in ['T1','T2','T3','T4']:
   start=len(r['events']);s.tap(s.code(track),hold_ms=20,after_ms=30);s.tap(s.code('1'),hold_ms=40,after_ms=100);mark(track+' panel press release',start)
  r.update(passed=s.halted is None and mi.received==mi.delivered,halted=s.halted,received=mi.received,delivered=mi.delivered)
 except Exception:r.update(passed=False,failure=traceback.format_exc())
 finally:
  if s:s.close()
 print(mode,r.get('passed'),flush=True)
report['passed']=all(c['passed'] for c in report['cases'])
Path('outputs/Digitone-E04-PC-input-live-sustain-panel.json').write_text(json.dumps(report,indent=2))
if not report['passed']:raise SystemExit(1)


