"""Differential resolver/read checks plus the existing four-track hook ABI test."""
import pathlib,sys,json,struct,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn.m68k_const import *
RAM,PTR,BSS=0x47be0000,0x47be1000,0x47be1004
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(7)]+[UC_M68K_REG_SR]
machines=[]
for name in ['fast-pitch-overlay','compact-hook-overlay']:
 m=Machine(ddr=0x08000000);m.ensure(RAM);m.ensure(0x47bccf04);m.ensure(0x47fdff00)
 b=pathlib.Path('work/'+name+'.bin').read_bytes();m.uc.mem_write(RAM,b);m.install_isa_patches_scoped(b[:1892],RAM);machines.append(m)
comparisons=0
def observed_registers(m):
 values=[m.uc.reg_read(reg) for reg in regs[:-1]]
 # Materialize condition codes in guest code; reg_read(SR) alone can expose
 # stale lazy flags in this engine.
 m.uc.mem_write(0x47fdfd00,bytes.fromhex('40c7'))
 m.uc.emu_start(0x47fdfd00,0x47fdfd02,count=1)
 return values+[m.uc.reg_read(UC_M68K_REG_D7)&0xffff]
for track in [0,1,2,3,4,127,0xffffffff]:
 for bad in [-1,0,1,2,3,4]:
  results=[]
  for m in machines:
   uc=m.uc;header=[0x534c4332,2,0xb70,1]
   if 0<=bad<=3:header[bad]^=1
   uc.mem_write(PTR,struct.pack('>I',0 if bad==4 else BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',*header))
   for i,reg in enumerate(regs[:-1]):uc.reg_write(reg,0x24680100+i)
   uc.reg_write(UC_M68K_REG_D0,track)
   call(m,layout['resolve']['address'],[],stack_top=0x47fdff00,limit=1000)
   assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   results.append(observed_registers(m))
  assert results[0]==results[1],('resolve',track,bad,results);comparisons+=1
for track in [0,1,2,3,4,0xffffffff]:
 for bad in [-1,0,1,2,3]:
  results=[]
  for m in machines:
   uc=m.uc;record=BSS+0xb30;identity=0x419c38c0;values=[identity,0x800000bd,0,0x80000000|track]
   if bad==0:values[0]+=4
   if bad==1:values[2]=1
   if bad==2:values[3]^=1
   for i,v in enumerate(values):uc.mem_write(record+i*4,struct.pack('>I',v))
   for i,reg in enumerate(regs[:-1]):uc.reg_write(reg,0x24680100+i)
   call(m,layout['read']['address'],[record,0 if bad==3 else identity,track],stack_top=0x47fdff00,limit=1000)
   assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   results.append(observed_registers(m))
  assert results[0]==results[1],('read',track,bad,results);comparisons+=1
out={'firmware_modified':False,'resolver_and_read_differential_cases':comparisons,'all_registers_and_flags_match':True,'build':json.loads(pathlib.Path('work/compact-hook-build.json').read_text())}
pathlib.Path('outputs/Digitone-compact-hook-helper-checks.json').write_text(json.dumps(out,indent=2));print('PASS differential',comparisons,flush=True)
source=pathlib.Path('work/test-fast-pitch-hook-ABI.py').read_text().replace('work/fast-pitch-overlay.bin','work/compact-hook-overlay.bin').replace('outputs/Digitone-fast-pitch-hook-ABI.json','outputs/Digitone-compact-hook-ABI.json')
exec(compile(source,'compact-hook-ABI','exec'))
