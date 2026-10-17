import pathlib,sys
sys.path.insert(0,str(pathlib.Path('work/disassembly-deps').resolve()))
from capstone import *
c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
data=pathlib.Path('work/section-3.bin').read_bytes();b=0x40000400
for a,n in [(0x40001dd6,200),(0x400028b0,90),(0x40002cb0,90),(0x4008c550,80),(0x40206ac0,70)]:
 for i in c.disasm(data[a-b:a-b+n],a):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
