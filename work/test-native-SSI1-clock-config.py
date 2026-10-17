import sys,pathlib,json
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu.harness import Machine
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_SR,UC_M68K_REG_PC
stock=pathlib.Path('work/section-3.bin').read_bytes();m=Machine(ddr=128<<20)
for a in (0x40000000,0x80000000,0xfc000000,0xec000000):m.ensure(a)
for a in range(0x40000000,0x40250000,0x1000):m.ensure(a)
m.ensure(0xec09000e);m.ensure(0xfc0c8024)
m.uc.mem_write(0x40000400,stock);m.install_isa_patches_scoped(stock,0x40000400)
checks=[]
for initial in (0,0xffff,0x30,0x0800):
 m.uc.reg_write(UC_M68K_REG_A7,0x8000fff0);m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.mem_write(0xec09000e,initial.to_bytes(2,'big'))
 m.uc.emu_start(0x40000f66,0x40000f9c,count=100000)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0x40000f9c
 result=int.from_bytes(m.uc.mem_read(0xec09000e,2),'big');assert result==initial&0xffcf
 checks.append(dict(test='Actual mask producer, memset call, and source write',initial=hex(initial),result=hex(result)))
for flag,expected in [(0,0x16101),(0x80000,0x56103)]:
 m.uc.reg_write(UC_M68K_REG_A7,0x8000fff0);m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.mem_write(0x401f21e0,flag.to_bytes(4,'big'));m.uc.mem_write(0xfc0c8024,(0x40000).to_bytes(4,'big'))
 m.uc.emu_start(0x40000fbc,0x40001152,count=100000)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0x40001152
 result=int.from_bytes(m.uc.mem_read(0xfc0c8024,4),'big');assert result==expected
 checks.append(dict(test='Actual board branch configures CCR',board_flag=hex(flag),result=hex(result)))
pathlib.Path('outputs/Digitone-SSI1-native-source-divider-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,firmware_modified=False,scope='Native stock initialization slices with supplied reset values and board flags; does not identify physical board'),indent=2));print('Passed',len(checks),'stock source/divider execution checks')
