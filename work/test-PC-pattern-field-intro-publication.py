from pathlib import Path
import sys,os,json,struct,shutil,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,sparse
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
rd=lambda u,a:int.from_bytes(u.mem_read(a,4),'big')
start=json.loads(Path('outputs/Digitone-E04-PC-resident-deferred-startup-startup.json').read_text());case=next(x for x in start['cases'] if x['image']=='E04_restored');original_root=Path(case['ui_snapshot']).parents[2];syx=Path('outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx').resolve();original_paths=bs.FirmwarePaths(str(original_root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));root=Path('work/PC-pattern-owner-intro-audit').resolve();root.mkdir(exist_ok=True);paths=bs.FirmwarePaths(str(root),syx.name,original_paths.devices_dir)
for directory in ['sections','devices']:shutil.copytree(original_root/directory,root/directory,dirs_exist_ok=True)
with open(original_paths.card,'rb') as src,open(paths.card,'wb') as dst:
 sparse.make_sparse(dst);sparse.extend(dst,Path(original_paths.card).stat().st_size)
 while chunk:=src.read(1024*1024):
  if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
os.environ.update(paths.env());os.environ['DT2_SYX']=str(syx)
r={'PC_only':True,'source_snapshot':original_paths.cold,'source_card_cloned':True,'events':[],'field_writes':[],'failure':None}
def observe(m,ev,stage):
 u=m.uc;r['initial_field']=hex(rd(u,0x41a720f0));r['initial_object_vtable']=hex(rd(u,0x41a720d0))
 for a,n in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280),(0x47fa0600,492),(0x47fa0900,594),(0x47fa0c00,750)]:m.install_isa_patches_scoped(bytes(u.mem_read(a,n)),a)
 def record(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);args=struct.unpack('>IIII',u.mem_read(sp,16));row={'pc':hex(pc),'caller':hex(args[0]),'object':hex(args[1]),'arg2':hex(args[2]),'arg3':hex(args[3]),'sp':hex(sp),'a6':hex(u.reg_read(UC_M68K_REG_A6))}
  if 0x40000000<=args[1]<0x48000000:row['field_before']=hex(rd(u,args[1]+32));row['vtable']=hex(rd(u,args[1]))
  r['events'].append(row)
 for pc in [0x40152ffe,0x40153060,0x40153078,0x4002f6be,0x4002f80c,0x4002c1d2]:u.hook_add(UC_HOOK_CODE,record,begin=pc,end=pc)
 def fieldwrite(u,access,a,n,v,d):
  canonical=0x40000000+(a-0x40000000)%0x08000000
  if canonical<0x41a720f4 and canonical+n>0x41a720f0:r['field_writes'].append({'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'bytes':n,'value':hex(v),'before':hex(rd(u,0x41a720f0))})
 for alias in range(8):u.hook_add(UC_HOOK_MEM_WRITE,fieldwrite,begin=0x41a720ef+alias*0x08000000,end=0x41a720f4+alias*0x08000000)
try:
 result=bs.boot_to_ui(str(syx),original_paths.cold,out=str(root/'intro-field-audit.snap'),budget=400_000_000,fast=True,options={'ddr':0x08000000,'unblock':False,'on_machine':observe});r.update(passed=result.up,intro_done=result.intro_done,mainloop=result.mainloop)
 assert result.up
except Exception:r.update(passed=False,failure=traceback.format_exc());print(r['failure'],flush=True)
r['limits']=['Replay from a cold parked checkpoint with an isolated clone of the current associated emulator card; not a fresh full loader/cold execution.','Inherited boot and GUI shortcut/clock assumptions remain; no physical timing or exception cleanup proof.']
Path('outputs/Digitone-E04-PC-pattern-field-intro-publication.json').write_text(json.dumps(r,indent=2));print('INTRO',r['passed'],'events',len(r['events']),'writes',len(r['field_writes']),flush=True)
if not r['passed']:raise SystemExit(1)
