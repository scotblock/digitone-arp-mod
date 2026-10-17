from pathlib import Path
source=Path('work/test-E08D-owner-guards.py').read_text().replace('E08D','E08E')
exec(compile(source,'E08E-owner-contracts','exec'))
from unicorn.m68k_const import *

put(S+8,1);put(S+12,1);put(S+16,3);put(S+20,2);put(S+280,1)
u.mem_write(S+96,b'\x01'*128);arena=bytes(u.mem_read(n['arena'],64))
owner=get(S+336);invoke(0x47be7400)
assert [get(S+x) for x in [8,12,16,20]]==[0,0,0,0]
assert bytes(u.mem_read(S+96,128))==bytes(128)
assert get(S+280)==1 and get(S+336)==owner and bytes(u.mem_read(n['arena'],64))==arena
put(0x47be2840,0x434f4c44);before=bytes(u.mem_read(S,344));invoke(0x47be7400)
assert bytes(u.mem_read(S,344))==before
put(0x47be2840,0x4c495645);put(S+8,1);put(S+12,1);put(S+16,3)
put(0x419b3cfc,0x43201234)
regs=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+7))
for reg in regs:u.reg_write(reg,0x12340000+reg)
u.reg_write(UC_M68K_REG_SR,0x2300);u.reg_write(UC_M68K_REG_A7,ST)
before={reg:u.reg_read(reg) for reg in regs}
u.emu_start(0x47be7480,0x400f4af2,count=10000)
assert u.reg_read(UC_M68K_REG_PC)==0x400f4af2 and u.reg_read(UC_M68K_REG_A7)==ST
assert u.reg_read(UC_M68K_REG_SR)==0x2300
assert u.reg_read(UC_M68K_REG_A2)==0x43201234
assert all(u.reg_read(reg)==v for reg,v in before.items() if reg!=UC_M68K_REG_A2)
result={'PC_only':True,'passed':True,'strict_ColdFire_checked':True,
 'quiesce_clears_generation_and_members':True,'busy_arena_and_owner_preserved':True,
 'COLD_refuses_mutation':True,'stock_command_bridge_register_stack_and_IPL_preserved':True,
 'stock_displaced_MOVEA_replayed':True}
Path('outputs/Digitone-E08E-stop-guard-contracts.json').write_text(json.dumps(result,indent=2));print(result)
