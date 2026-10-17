from pathlib import Path
import sys,json
sys.path.insert(0,'work/emulator-deps')
from capstone import *
d=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
for p,n in [(0x4018ab5e,80),(0x4001d65a,65),(0x400e9444,88)]:
 print(hex(p));items=list(cs.disasm(d[p-base:p-base+n],p))
 for i in items:print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
