"""PC control: call stock cache flush on the native saved-project state.

The entry is explicitly invoked by this harness, not by an emulated power-loss
interrupt. No cache contents, pending bank, or flash bytes are host-inserted.
"""
from pathlib import Path
import json, os, shutil, sys, traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu','work']
from emu import bootstrap as bs, sparse, longrun
from emu.session import Session
from unicorn.m68k_const import UC_M68K_REG_A7, UC_M68K_REG_PC
from E10_storage_probe import record_bytes

original_build=longrun.build
def build(*args,**kwargs):
 kwargs['unblock']=False
 return original_build(*args,**kwargs)
longrun.build=build

proof=json.loads(Path('outputs/Digitone-E10-PC-persistence-native-save-load.json').read_text())
assert proof['passed'] and proof['native_retained_mirror_records_match']==128
syx=Path('work/os144/E09A-PC-path-candidate.syx').resolve()
root=Path('work/E10-persistence-explicit-cache-flush').resolve();root.mkdir(exist_ok=True)
paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()))
srcpaths=bs.FirmwarePaths(str(Path('work/E10-persistence-save-load').resolve()),syx.name,paths.devices_dir)
shutil.copytree(srcpaths.sections,paths.sections,dirs_exist_ok=True)
shutil.copytree(srcpaths.overlay,paths.overlay,dirs_exist_ok=True);shutil.copyfile(syx,paths.syx)
with open(srcpaths.card,'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(srcpaths.card).stat().st_size)
 while chunk:=src.read(1024*1024):
  if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env())
rd=lambda u,a:int.from_bytes(u.mem_read(a,4),'big')
out=dict(PC_only=True,passed=False,explicit_host_entry=True,power_loss_interrupt_emulated=False,cache_contents_host_written=False,writes=[],failure=None)
s=Session(proof['post_save_snapshot'],syx=str(syx),ddr=0x8000000,audio=True)
returned=False
try:
 u=s.m.uc;pending=rd(u,0x402369e0);selected=rd(u,0x402369e4)
 out.update(pending_bank=pending,selected_bank=selected)
 assert pending in [0,1] and pending!=selected
 dest=rd(u,0x401c2de0+pending*4)*512
 out['destination']=hex(dest)
 ret=s.pc;sp=u.reg_read(UC_M68K_REG_A7)
 def back(u,pc,n,d):
  global returned
  # A harness stop marker lets spin return immediately. Repeatedly stopping
  # at an unchanged PC would otherwise consume its budget one hook at a time.
  returned=True;s.m.halt_vec=-1;u.emu_stop()
 def writer(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7)
  out['writes'].append(dict(sector=rd(u,sp+4),length=rd(u,sp+8),source=hex(rd(u,sp+12))))
 s.at(ret,back);s.at(0x400a793e,writer)
 # One native call frame is a disclosed execution fixture. It changes no
 # project/bank metadata, serialized data, or storage-controller result.
 u.mem_write(sp-4,ret.to_bytes(4,'big'));u.reg_write(UC_M68K_REG_A7,sp-4)
 s.pc=0x400a8182;u.reg_write(UC_M68K_REG_PC,s.pc)
 for _ in range(100):
  s.run_ms(100)
  if returned or s.halted:break
 assert returned,('Stock flush did not return',s.halted,hex(s.pc))
 assert rd(u,0x402369e0)==0xffffffff
 s.ev['esdhc'].card.flush()
 with open(paths.card,'rb') as f:
  f.seek(dest);assert f.read(4)==b'COKI'
  matches=[]
  for i in range(128):
   f.seek(dest+0x110+0x240200+i*0xa00+0x940);matches.append(f.read(32)==record_bytes(i))
  f.seek(rd(u,0x401c2de0+selected*4)*512);out['old_bank_magic']=f.read(4).hex()
 out['records_match']=sum(matches);assert all(matches)
 out.update(passed=True,card=paths.card)
except Exception:
 out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 s.close()
 out['limits']=['The stock writer entry is invoked explicitly in a PC fixture. Automatic shutdown/power-fail dispatch and physical persistence are not established.','Input records come from the preceding native load/save session; no record/bank/cache data are host-inserted in this control.']
 Path('outputs/Digitone-E10-PC-persistence-explicit-cache-flush.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2),flush=True)
if not out['passed']:raise SystemExit(1)
