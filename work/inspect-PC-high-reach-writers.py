from pathlib import Path
import sys
sys.path.insert(0,'work/emulator-deps')
from capstone import *
d=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
for a,n in [(0x4000045c,0x56),(0x400004b2,0x34),(0x400fbb20,0x74),(0x400fbad8,0x48),(0x400e96c0,0x30)]:
 print('\nTARGET',hex(a))
 for i in cs.disasm(d[a-base:a-base+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
