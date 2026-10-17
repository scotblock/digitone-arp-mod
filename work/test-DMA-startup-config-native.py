import sys,pathlib,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu.harness import Machine
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_SR
stock=pathlib.Path('work/section-3.bin').read_bytes();lo,hi=0x40000546,0x40000554
code=stock[lo-0x40000400:hi-0x40000400];out={'cases':[],'firmware_modified':False,'code':code.hex()}
for seed in [0,0xe400,0xe440,0xe408,0xe4c0]:
 m=Machine(ddr=128<<20);m.ensure(lo);m.ensure(0xfc044000);m.ensure(0x80000000)
 m.uc.mem_write(lo,code);m.uc.mem_write(0xfc044000,struct.pack('>I',seed));m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,0x8000fff0)
 m.uc.emu_start(lo,hi);got=struct.unpack('>I',m.uc.mem_read(0xfc044000,4))[0]
 assert got==seed|6
 out['cases'].append({'inherited':hex(seed),'result':hex(got),'CLM':bool(got&64),'ERCA':bool(got&4),'ERGA':bool(got&8),'EMLM':bool(got&128)})
pathlib.Path('outputs/Digitone-DMA-startup-config-native.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
