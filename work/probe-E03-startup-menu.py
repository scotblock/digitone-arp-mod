from pathlib import Path
import sys,json,time
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom,longrun
from dt2.elz import depack_section
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_D0
import struct
s='outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx'
original=longrun.spin
def fast(*a,**kw):kw['fast']=True;return original(*a,**kw)
longrun.spin=fast
hits=[]
def install(m,flash,dspi):
 def menu(uc,pc,n,d):hits.append(hex(pc));m.halt_vec=-2;uc.emu_stop()
 m.menu_hook=m.uc.hook_add(UC_HOOK_CODE,menu,begin=0x80002162,end=0x80002162)
start=time.time();r=bootrom.boot(s,depack_section(bootrom.container_section(s,2)),Path('work/os144/emulator-E02-main.bin').read_bytes(),held={0:4},ui_card=8,straps={0xec09401b:8},groups=7,limit=80000000,chunk=1000000,on_machine=install)
out={'PC_only':True,'held_FUNC_fixture':True,'stop':r.stop,'pc':hex(r.m.uc.reg_read(UC_M68K_REG_PC)),'MAIN_reached':r.reached,'instructions':r.instructions,'flash_writes':r.flash_writes,'seconds':time.time()-start,'panel_queries':r.panel_queries,'boot_key_bitmap':bytes(r.m.uc.mem_read(0x8000771e,16)).hex(),'limits':['Bounded startup probe with PLL/DDR/DSPI/panel models; no MIDI bytes sent and no device accessed.']}
out['startup_menu_entry_hits']=hits;out['actual_boot_key_bitmap']=bytes(r.m.uc.mem_read(0x80008052,16)).hex()
if hits:
 m=r.m;m.halt_vec=None;m.uc.hook_del(m.menu_hook)
 def key(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret,ptr=struct.unpack('>II',uc.mem_read(sp,8));uc.mem_write(ptr,bytes(4)+bytes([29,0,1,0]));uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,key,begin=0x80001428,end=0x80001428)
 def upgrade(uc,pc,n,d):m.halt_vec=-3;uc.emu_stop()
 m.uc.hook_add(UC_HOOK_CODE,upgrade,begin=0x800041a6,end=0x800041a6)
 pc,n,why=longrun.spin(m,0x80002162,5000000,chunk=1000000)
 out['TRIG4_selection_fixture']={'key_event_code':29,'reached':hex(pc),'instructions':n,'stop':why,'upgrade_entry_reached':pc==0x800041a6};assert pc==0x800041a6
 out['flash_writes_after_selection']=list(r.flash.writes);assert not r.flash.writes
Path('outputs/Digitone-E03-startup-menu-probe.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
