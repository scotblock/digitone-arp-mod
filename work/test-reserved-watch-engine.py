"""Check the native engine's actual computed and bulk write watch routing."""
import sys,json,pathlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_A0,UC_M68K_REG_D1,UC_M68K_REG_PC,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7
RAM=0x47be0000;checks=[]
def check(label,ok):assert ok,label;checks.append(label)
for k in range(8):
 m=Machine(ddr=0x08000000);a=RAM+k*0x08000000;m.ensure(a);m.ensure(RAM);m.load(bytes.fromhex('2081 4e71'),0x40001000);hits=[]
 m.uc.hook_add(UC_HOOK_MEM_WRITE,lambda uc,t,a,n,v,d:hits.append((a,n,v,uc.reg_read(UC_M68K_REG_PC))),begin=a,end=a+0x1ffff)
 m.uc.reg_write(UC_M68K_REG_A0,a+0x1004);m.uc.reg_write(UC_M68K_REG_D1,0x12345678);m.uc.emu_start(0x40001000,0,count=1)
 check(f'computed write detected alias {k}',hits==[(a+0x1004,4,0x12345678,0x40001000)])
 check(f'computed write shares cached bytes alias {k}',bytes(m.uc.mem_read(RAM+0x1004,4))==bytes.fromhex('12345678'))
 m.close()
m=Machine(ddr=0x08000000);m.ensure(RAM);m.load(bytes.fromhex('48d000f0 4e71'),0x40001000);hits=[]
m.uc.hook_add(UC_HOOK_MEM_WRITE,lambda uc,t,a,n,v,d:hits.append((a,n,v)),begin=RAM-64,end=RAM+0x2003f)
m.uc.reg_write(UC_M68K_REG_A0,RAM+0x1004)
for j,reg in enumerate([UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7]):m.uc.reg_write(reg,0x100+j)
m.uc.emu_start(0x40001000,0,count=1)
check('bulk MOVEM writes all observed',hits==[(RAM+0x1004+4*j,4,0x100+j) for j in range(4)])
m.close()
m=Machine(ddr=0x08000000);m.ensure(RAM);m.load(bytes.fromhex('2081 4e71'),0x40001000);hits=[]
m.uc.hook_add(UC_HOOK_MEM_WRITE,lambda uc,t,a,n,v,d:hits.append((a,n,v)),begin=RAM-64,end=RAM+0x2003f)
m.uc.reg_write(UC_M68K_REG_A0,RAM-2);m.uc.reg_write(UC_M68K_REG_D1,0x12345678);m.uc.emu_start(0x40001000,0,count=1)
check('write straddling lower interval edge observed',hits==[(RAM-2,4,0x12345678)])
m.close()
pathlib.Path('outputs/Digitone-native-write-watch-tests.json').write_text(json.dumps({'checks':checks,'check_count':len(checks),'firmware_modified':False},indent=2));print('PASS',len(checks),'native write watch assertions')
