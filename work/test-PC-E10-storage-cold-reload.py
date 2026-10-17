"""Load the saved named project after a fresh native boot; never seed data."""
from pathlib import Path
import json,os,sys,shutil,traceback
prefix=Path('work/test-E09A-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(prefix,'E10-cold-reload-definitions','exec'))
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
from emu import sparse
from unicorn.m68k_const import UC_M68K_REG_A5,UC_M68K_REG_D3
proof=json.loads(Path('outputs/Digitone-E10-PC-storage-cold-startup.json').read_text());assert proof['passed'];case=proof['cases'][0]
source_paths=bs.FirmwarePaths(str(Path(case['ui_snapshot']).parents[2]),syx.name,str(Path('work/upstream/digiemu/devices').resolve()))
root=Path('work/E10-storage-cold-reload').resolve();root.mkdir(exist_ok=True)
paths=bs.FirmwarePaths(str(root),syx.name,source_paths.devices_dir)
shutil.copytree(source_paths.sections,paths.sections,dirs_exist_ok=True);shutil.copytree(source_paths.overlay,paths.overlay,dirs_exist_ok=True);shutil.copyfile(syx,paths.syx)
with open(source_paths.card,'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(source_paths.card).stat().st_size)
 while chunk:=src.read(1024*1024):
  if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env());phase='warm'
out.update(steps=[],load_records=[],diagnostic_record_host_injection=False,code_overlay=False,firmware_container_created=False,failure=None)
original_install=install
def install(s):
 original_install(s)
 def decoded(u,pc,n,d):
  if phase!='load':return
  offset=u.reg_read(UC_M68K_REG_D3);assert offset%0xa00==0;slot=offset//0xa00;assert slot<128
  address=u.reg_read(UC_M68K_REG_A5)+offset;data=bytes(u.mem_read(address+0x940,32))
  out['load_records'].append(dict(slot=slot,matches=data==record_bytes(slot),actual=data.hex()))
 s.at(0x4000e960,decoded)
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def tap(key,wait=300):s.tap(s.code(key),hold_ms=100,after_ms=wait)
def mark(label):
 out['steps'].append(dict(label=label,ms=s.now_ms(),records=len(out['load_records'])))
 if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-storage-cold-reload-'+label+'.png',4)
 print(label,len(out['load_records']),flush=True)
try:
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  t=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);t.now=s.pits.now;s.pits.sources=s.pits.sources+(t,)
 s.run_ms(1000);tap('STOP',200);mark('ready')
 # Cold boot resets the selector to slot 001 PRESETS. The diagnostic project
 # was saved explicitly to slot 002 NEW PROJECT, so choose that row here.
 phase='load';tap('GLOBAL');mark('settings');tap('YES');mark('menu');tap('YES');mark('selector');tap('DOWN');mark('slot_002');tap('YES',2000);mark('selected')
 # The cold working copy asks whether to save before loading. Choose NO so
 # the diagnostic file is loaded without entering another Save As workflow.
 tap('NO',300);mark('discard_confirm');tap('YES',800)
 for _ in range(12):
  if len({x['slot'] for x in out['load_records']})==128:break
  s.run_ms(250)
 mark('confirm');out['preload_save_prompt_answer']='NO';out['discard_confirmation_answer']='YES'
 rows={x['slot']:x for x in out['load_records']};out.update(all_128_slots_reached=set(rows)==set(range(128)),all_records_recovered=len(rows)==128 and all(x['matches'] for x in rows.values()),halted=s.halted)
 assert out['all_128_slots_reached'] and out['all_records_recovered'] and s.halted is None
 s.ev['esdhc'].card.flush();preserved(s);out['passed']=True
except Exception:out.update(passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
finally:
 s.close();out['limits']=['Named-project reload after actual native cold boot, on a separate emulator card. No diagnostic data or executable code is inserted in either stage.','The unmodified decoder ignores the extension. This verifies stored serialized bytes, not restored E10 arp state or automatic working-cache preservation.','Physical storage, cache coherence, concurrent loads and copy/clear remain outside this test.']
 Path('outputs/Digitone-E10-PC-storage-cold-reload.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
