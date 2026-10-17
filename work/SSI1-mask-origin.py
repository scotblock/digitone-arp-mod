import pathlib,sys
sys.path.insert(0,str(pathlib.Path('work/disassembly-deps').resolve()))
from capstone import *
c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE);d=pathlib.Path('work/section-3.bin').read_bytes();b=0x40000400
for i in c.disasm(d[0x40000e9a-b:0x40000f38-b],0x40000e9a):print(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
