from pathlib import Path
import sys,json,struct,time,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom,longrun
from dt2.elz import depack_section
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
syx=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx');main=Path('work/os144/emulator-E02-main.bin').read_bytes();blob=Path('work/os144/packed-context-overlay.bin').read_bytes();stage=0x4029c4b0
originalspin=longrun.spin
def fastspin(*args,**kwargs):kwargs['fast']=True;return originalspin(*args,**kwargs)
longrun.spin=fastspin
out={'PC_only':True,'image_sha256':hashlib.sha256(syx.read_bytes()).hexdigest(),'events':[],'copier_stores':0,'failure':None,'limits':['Serial hardware boot represented by stock bootstrap in SRAM.','Flash identification, DSPI, PLL, DDR and panel hardware are modeled.','Cache-control registers are traced; physical cache coherence is not emulated.','No firmware receiving/update session is executed.']};start=time.monotonic()
def install(m,flash,dspi):
 uc=m.uc;m.install_isa_patches_scoped(main,0x40000400);m.install_isa_patches_scoped(blob[:1784],0x47be0000)
 def boundary(uc,pc,n,d):
  rec={'pc':hex(pc),'cache_controls':{hex(k):hex(v) for k,v in m.ctlregs.items()}}
  if pc==stage:assert bytes(uc.mem_read(stage+256,len(blob)))==blob;rec['source_intact']=True
  if pc in [0x4000053e,0x40000568]:assert bytes(uc.mem_read(0x47be0000,len(blob)))==blob;rec['copied_code_exact']=True
  if pc==0x4000053e:
   rec['header']=list(struct.unpack('>IIII',uc.mem_read(0x47be1004,16)));assert rec['header']==[0x534c4332,2,0xb70,0]
  out['events'].append(rec)
  if pc==0x40000568:m.halt_vec=-2;uc.emu_stop()
 for pc in [stage,0x4000053e,0x40000568]:uc.hook_add(UC_HOOK_CODE,boundary,begin=pc,end=pc)
 def store(uc,access,a,n,v,d):
  assert stage<=uc.reg_read(UC_M68K_REG_PC)<stage+94
  assert not m.ctlregs[2]&0xa0000000
  out['copier_stores']+=1
 uc.hook_add(UC_HOOK_MEM_WRITE,store,begin=0x47be0000,end=0x47be0000+len(blob)-1)
try:
 r=bootrom.boot(str(syx),depack_section(bootrom.container_section(str(syx),2)),main,limit=300000000,chunk=10000000,on_machine=install,trace=lambda m,n,pc:print('loader',n,hex(pc),flush=True),ui_card=8,straps={0xec09401b:8},groups=7)
 out['loader']={'stop':r.stop,'reached':hex(r.reached) if r.reached else None,'main_matches':r.main_os_matches,'instructions':r.instructions,'flash_writes':r.flash_writes,'flags':r.boot_flags,'cache_controls':{hex(k):hex(v) for k,v in r.m.ctlregs.items()}}
 assert r.reached==0x400004e8 and r.main_os_matches and not r.flash_writes
 r.m.halt_vec=None
 pc,n,stop=longrun.spin(r.m,r.reached,100000000,chunk=10000000)
 out['application_prefix']={'pc':hex(pc),'instructions':n,'stop':stop,'copied_exact':bytes(r.m.uc.mem_read(0x47be0000,len(blob)))==blob}
 assert pc==0x40000568 and out['copier_stores']==len(blob)//4
 out['passed']=True
except BaseException:
 out['passed']=False;out['failure']=traceback.format_exc();print(out['failure'],flush=True)
out['seconds']=time.monotonic()-start;Path('outputs/Digitone-OS1.44E03-stock-loader-check.json').write_text(json.dumps(out,indent=2));print('loader result',out['passed'],out['seconds'],flush=True)
