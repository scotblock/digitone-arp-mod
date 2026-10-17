"""Probe +0x940 kit-slot storage through native panel save/load on a private card.

Diagnostic records are host-written after native serialization. No executable,
firmware container, runtime arp settings or real user project is modified.
"""
from pathlib import Path
import json,sys,os,shutil,struct,hashlib,traceback
prefix=Path('work/test-E09A-packaged-panel-playback.py').read_text().split('\ns = Session(')[0]
exec(compile(prefix,'E10-storage-native-session-definitions','exec'))
from emu import sparse
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_D3,UC_M68K_REG_D7,UC_M68K_REG_PC

private=Path('work/E10-storage-save-load').resolve();private.mkdir(exist_ok=True)
original_paths=paths
paths=bs.FirmwarePaths(str(private),syx.name,str(Path('work/upstream/digiemu/devices').resolve()))
shutil.copytree(original_paths.sections,paths.sections,dirs_exist_ok=True)
shutil.copytree(original_paths.overlay,paths.overlay,dirs_exist_ok=True)
shutil.copyfile(syx,paths.syx)
with open(original_paths.card,'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(original_paths.card).stat().st_size)
 while data:=src.read(1024*1024):
  if data.strip(b'\0'):dst.seek(src.tell()-len(data));dst.write(data)
os.environ.update(paths.env())
out.update(test='serialized kit +0x940..+0x95f native save/load',diagnostic_record_host_injection=True,executable_overlays=False,
           E10_arp_integration=False,save_records=[],load_records=[],candidate_writes=[],steps=[],private_card=str(Path(paths.card).relative_to(Path.cwd())),failure=None)
encoded_base=None;watch_installed=False;injected=set();phase='setup'
sys.path.insert(0,'work')
from E10_storage_probe import record_bytes
base_install=install
def install(s):
 base_install(s)
 def encoded(u,pc,n,d):
  global encoded_base,watch_installed
  if phase!='save':return
  offset=u.reg_read(UC_M68K_REG_D7);address=u.reg_read(UC_M68K_REG_A4)
  assert offset%0x988==0;slot=offset//0x988;assert 0<=slot<128
  encoded_base=address-slot*0xa00
  if not watch_installed:
   def write(uc,access,a,size,value,data):
    rel=a-encoded_base;part=rel%0xa00
    if part<0x960 and part+size>0x940 and len(out['candidate_writes'])<200:
     out['candidate_writes'].append(dict(phase=phase,slot=rel//0xa00,offset=hex(part),size=size,pc=hex(uc.reg_read(UC_M68K_REG_PC))))
   u.hook_add(UC_HOOK_MEM_WRITE,write,begin=encoded_base,end=encoded_base+0x50000-1);watch_installed=True
  before=bytes(u.mem_read(address,0xa00));u.mem_write(address+0x940,record_bytes(slot));after=bytes(u.mem_read(address,0xa00))
  assert before[:0x940]==after[:0x940] and before[0x960:]==after[0x960:]
  out['save_records'].append(dict(slot=slot,base=hex(address),previous_sha256=hashlib.sha256(before[0x940:0x960]).hexdigest()))
  injected.add(slot)
 def decoding(u,pc,n,d):
  if phase!='load':return
  offset=u.reg_read(UC_M68K_REG_D3);assert offset%0xa00==0;slot=offset//0xa00
  address=u.reg_read(UC_M68K_REG_A5)+offset;actual=bytes(u.mem_read(address+0x940,32))
  out['load_records'].append(dict(slot=slot,base=hex(address),matches=actual==record_bytes(slot),actual=actual.hex()))
 s.at(0x4000ece0,encoded);s.at(0x4000e960,decoding)

s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x8000000,audio=True,on_machine=install)
def mark(label):
 out['steps'].append(dict(label=label,ms=s.now_ms(),saved=len(out['save_records']),loaded=len(out['load_records'])))
 if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-storage-'+label+'.png',4)
 print(label,len(out['save_records']),len(out['load_records']),flush=True)
 Path('outputs/Digitone-E10-PC-storage-save-load-progress.json').write_text(json.dumps(out,indent=2))
def tap(key,wait=300):s.tap(s.code(key),hold_ms=100,after_ms=wait)
try:
 if not any(1 in getattr(t,'channels',()) for t in s.pits.sources):
  timer=Dtims(s.m,channels=(1,),instr_per_sec=s.ips,clear_stale=False);timer.now=s.pits.now;s.pits.sources=s.pits.sources+(timer,)
 s.run_ms(6500);tap('STOP',200);mark('ready')
 phase='save';s.press(s.code('FUNC'));s.run_ms(100);tap('GLOBAL');s.release(s.code('FUNC'));s.run_ms(300);mark('save_menu')
 tap('YES',1500);mark('save_yes')
 tap('NO',200);tap('DOWN',200);tap('YES',1500);mark('save_empty')
 tap('YES',2000);s.run_ms(1000);mark('save_confirm')
 assert injected==set(range(128)),('Native save did not serialize all slots',sorted(injected))
 s.ev['esdhc'].card.flush()
 # Poison only the old temporary serialization buffer after saving. Reload
 # must recover the records from storage; this process will not inject again.
 phase='poison_saved_RAM'
 for slot in range(128):s.m.uc.mem_write(encoded_base+slot*0xa00+0x940,b'\xcc'*32)
 tap('NO',200)
 phase='load';tap('GLOBAL');mark('load_settings');tap('YES');mark('load_menu');tap('YES');mark('load_selector')
 tap('YES',2000);mark('load_selected');tap('YES',2000);s.run_ms(1500);mark('load_confirm')
 found={row['slot']:row for row in out['load_records']}
 out.update(all_128_native_load_slots_reached=set(found)==set(range(128)),all_records_recovered=len(found)==128 and all(row['matches'] for row in found.values()),halted=s.halted,encoded_buffer_poisoned_after_save=True)
 assert s.halted is None
 assert out['all_128_native_load_slots_reached'], 'No complete native reload witness'
 assert out['all_records_recovered'], 'Candidate bytes lost during native save/load'
 s.ev['esdhc'].card.flush();out['passed']=True
except Exception:
 out.update(passed=False,failure=traceback.format_exc());print(out['failure'],flush=True)
finally:
 s.close();out['limits']=['Diagnostic records are PC host writes at native serialize completion; no machine-code persistence helper is integrated.','Stopped panel save/reload only. Cold restoration, copy/clear and asynchronous replacement are separate checks.','No physical storage/cache/timing behavior is established.']
 Path('outputs/Digitone-E10-PC-storage-native-save-load.json').write_text(json.dumps(out,indent=2))
if not out.get('passed'):raise SystemExit(1)
