from pathlib import Path
import sys,json,struct,time,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
from dt2.container import decode_syx
stock=Path('work/os144/section-3.bin').read_bytes();raw=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx').read_bytes();wire=decode_syx('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx')
packets=[];i=0
while i<len(raw):j=raw.index(247,i+1);packets.append(raw[i:j+1]);i=j+1
STATE,DATA,MSG,STACK=0x40325ee0,0x40325f00,0x47f20000,0x47fdff00
u32=lambda x:struct.pack('>I',x&0xffffffff)
def machine():
 m=Machine(ddr=0x08000000);m.load(stock,0x40000400);m.install_isa_patches_scoped(stock,0x40000400)
 for a in [STATE,0x40400000,MSG,STACK,0x419950a4]:m.ensure(a)
 m.uc.mem_write(STATE,bytes(32));m.uc.mem_write(DATA,b'\xa5'*(len(wire)+512));m.notes=[]
 def notify(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret,q,msg=struct.unpack('>III',uc.mem_read(sp,12));m.notes.append({'type':bytes(uc.mem_read(msg,1))[0],'message':bytes(uc.mem_read(msg,9)).hex()})
  uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,notify,begin=0x40001cda,end=0x40001cda)
 call(m,0x400ed8dc,[],stack_top=STACK,limit=10000)
 return m
def feed(m,p):
 m.uc.mem_write(MSG,bytes(p));v=call(m,0x400e9fcc,[MSG,len(p)],stack_top=STACK,limit=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0;return v
def state(m):return {'phase':m.uc.mem_read(STATE,1)[0],'received':int.from_bytes(m.uc.mem_read(STATE+12,4),'big'),'total':int.from_bytes(m.uc.mem_read(STATE+8,4),'big'),'notices':[x['type'] for x in m.notes]}
