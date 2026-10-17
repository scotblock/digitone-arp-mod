"""Native panel edits/recall and saved-project reload; copied PC code only."""
from pathlib import Path
import json,os,shutil,traceback,sys
prefix=Path('work/test-E09A-packaged-panel-playback.py').read_text(encoding='utf-8').split('\ns = Session(')[0]
for old,new in [('outputs/Digitone-E09A-PC-path-layout.json','work/os144/PC_ONLY-E10-bound-full-layout.json'),("folder/'E09A-PC-install-layout.json'","folder/'PC_ONLY-E10-bound-layout.json'"),('outputs/Digitone-E09A-PC-startup-comparison.json','outputs/Digitone-E10-PC-bound-startup.json'),("folder/'E09A-PC-layout-payload.bin'","folder/'PC_ONLY-E10-bound-payload.bin'"),("folder/'E09A-PC-layout-main.bin'","folder/'PC_ONLY-E10-bound-main.bin'")]:prefix=prefix.replace(old,new)
prefix=prefix.replace("    for region in native['data_regions']:","    for region in native['data_regions']:\n        if region['name'] in ['E10_persistence_metadata','E10_pattern_binding_metadata']:continue")
exec(compile(prefix,'E10-bound-panel-definitions','exec'))
from emu import sparse
from emu.snapshot import save
from unicorn.m68k_const import UC_M68K_REG_A7
resume='--resume-load' in sys.argv
prior=json.loads(Path('outputs/Digitone-E10-PC-bound-panel-patterns.json').read_text()) if resume else None
source_paths=paths;root=Path('work/E10-bound-panel-patterns').resolve();root.mkdir(exist_ok=True)
paths=bs.FirmwarePaths(str(root),syx.name,source_paths.devices_dir)
if not resume:
 shutil.copytree(source_paths.sections,paths.sections,dirs_exist_ok=True);shutil.copytree(source_paths.overlay,paths.overlay,dirs_exist_ok=True);shutil.copyfile(syx,paths.syx)
 with open(source_paths.card,'rb') as src,open(paths.card,'wb') as dst:
  sparse.make_sparse(dst);sparse.extend(dst,Path(source_paths.card).stat().st_size)
  while chunk:=src.read(1024*1024):
   if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env());X=native['E10']['state'];BANK=native['E10']['bank'];BM=native['binding']['meta'];PM=native['persistence']['meta']
out.update(steps=[],native_calls=[],checkpoints={},bank_host_written=False,settings_host_written=False,diagnostic_record_host_injection=False,private_card=paths.card)
if resume:
 out.update(prior);out.update(passed=False,failure=None,resumed_from_native_load_confirmation=True)
 first_record,second_record=[bytes.fromhex(x) for x in out['expected_records']]
 first,second=out['expected_fields']
base_install=install
def install(s):
 base_install(s)
 for kind,address in list(native['binding']['entries'].items())+list(native['persistence']['entries'].items()):
  if kind not in ['recall','capture','emit']:continue
  def entered(u,pc,n,d,kind=kind):
   sp=u.reg_read(UC_M68K_REG_A7)
   out['native_calls'].append(dict(kind=kind,phase=phase,arg1=hex(rd(u,sp+4)),arg2=rd(u,sp+8),generation=rd(u,PM+12)))
  s.at(address,entered)
s=Session(prior['checkpoints']['load-selected'] if resume else case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def tap(key,wait=150):s.tap(s.code(key),hold_ms=80,after_ms=wait)
def combo(key):
 s.press(s.code('FUNC'));s.run_ms(80);tap(key);s.release(s.code('FUNC'));s.run_ms(150)
def owner():return rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x1008)
def fields():return [rd(s.m.uc,X+i) for i in [4,8,20,24]]+[bytes(s.m.uc.mem_read(X+32,16)).hex()]
def mark(label):
 row=dict(label=label,ms=s.now_ms(),owner=hex(owner()),bound_owner=hex(rd(s.m.uc,X+28)),slot=rd(s.m.uc,BM+8),generation=rd(s.m.uc,PM+12),fields=fields(),view=rd(s.m.uc,X+56),held=[rd(s.m.uc,S+i) for i in [8,16,280]])
 out['steps'].append(row)
 if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-bound-'+label+'.png',4)
 Path('outputs/Digitone-E10-PC-bound-panel-progress.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(label,row,flush=True)
def checkpoint(label):
 p=root/(label+'.snap');save(s.m,str(p),components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'));out['checkpoints'][label]=str(p)
def choose(number):
 s.press(s.code('PTN'));s.run_ms(80);tap(str(number),80);s.release(s.code('PTN'));s.run_ms(350)
def open_steps():
 combo('SYN2')
 if rd(s.m.uc,X+56)==0:s.turn(4,16,after_ms=150)
 assert rd(s.m.uc,X+56)==1 and rd(s.m.uc,X+28)==owner()
def valid_record(slot):
 raw=bytes(s.m.uc.mem_read(BANK+32*slot,32));assert raw[:4]==b'MS10' and sum(raw[:28])==int.from_bytes(raw[28:],'big');return raw
try:
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
 if not resume:
  s.run_ms(1000);tap('STOP');s.press(s.code('MIDI'));tap('T1');s.release(s.code('MIDI'));s.run_ms(150)
  phase='A01_edit';choose(1);tap('SYN1');combo('A');open_steps();mark('A01_blank')
  assert rd(s.m.uc,BM+8)==0 and rd(s.m.uc,X+4)==0
  s.turn(3,-16,after_ms=120);s.turn(6,16,after_ms=120);s.turn(8,16,after_ms=120)
  first=fields();first_record=valid_record(0);assert first[:2]==[1,15] and first[-1].startswith('01');mark('A01_edited')
  phase='A02_edit';tap('NO');choose(2);tap('SYN1');combo('A');open_steps();mark('A02_blank')
  assert rd(s.m.uc,BM+8)==1 and rd(s.m.uc,X+4)==0 and rd(s.m.uc,X+8)==16
  s.turn(1,16,after_ms=120);s.turn(6,-16,after_ms=120);s.turn(8,16,after_ms=120)
  second=fields();second_record=valid_record(1);assert second!=first and second[-1].startswith('ff');mark('A02_edited')
  tap('NO');choose(1);open_steps();assert fields()==first and valid_record(0)==first_record;mark('A01_recalled')
  tap('NO');choose(2);open_steps();assert fields()==second and valid_record(1)==second_record;mark('A02_recalled')
  out.update(two_pattern_panel_recall=True,expected_records=[first_record.hex(),second_record.hex()],expected_fields=[first,second])
  checkpoint('two-patterns-edited')
  # The same ordinary Save Project As sequence as the prior storage audit.
  phase='save';tap('NO');combo('GLOBAL');mark('save_menu');tap('YES',800);tap('NO');tap('DOWN');tap('YES',800);mark('save_name');tap('YES',2000);s.run_ms(700);mark('saved')
  assert any(x['kind']=='emit' and x['phase']=='save' for x in out['native_calls'])
  checkpoint('saved')
  # Change one step after saving, then load the saved file without saving again.
  for _ in range(3):tap('NO',80)
  phase='unsaved_edit';choose(1);open_steps();s.turn(6,16,after_ms=150);assert fields()!=first;mark('A01_unsaved_change');tap('NO')
 old_generation=rd(s.m.uc,PM+12);phase='reload'
 if not resume:tap('GLOBAL');tap('YES');tap('YES');mark('load_selector');tap('YES',1200);mark('load_selected');checkpoint('load-selected')
 tap('YES',1200);s.run_ms(700);mark('loaded')
 assert rd(s.m.uc,PM+12)>old_generation,'No completed native project capture on reload'
 assert bytes(s.m.uc.mem_read(BANK,64))==first_record+second_record,'Saved bank records did not replace unsaved edits'
 for _ in range(3):tap('NO',80)
 choose(1);open_steps();assert fields()==first;mark('A01_loaded_recall')
 tap('NO');choose(2);open_steps();assert fields()==second;mark('A02_loaded_recall')
 out.update(saved_project_reloaded=True,project_generation_changed=True,post_reload_pattern_recall=True)
 checkpoint('reloaded-two-patterns');s.ev['esdhc'].card.flush();preserved(s);assert s.halted is None
 out['passed']=True
except Exception:
 out.update(passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
finally:
 s.close();out['limits']=['Native panel-created records and native save/load on a private card, with copier-installed code. No bank/settings/helper/hook data are host-written.','Stopped pattern recall and project reload in this scenario. Running held-note handoff and physical behavior require separate checks.','Copy/clear/undo, incremental saves, physical cache/timing and automatic power-loss persistence remain unverified.']
 Path('outputs/Digitone-E10-PC-bound-panel-patterns.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
if not out.get('passed'):raise SystemExit(1)
