from pathlib import Path
import sys
sys.path.insert(0,'work/emulator-deps')
from capstone import *
b=0x40000400;d=Path('work/os144/section-3.bin').read_bytes();c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
for a,n in [(0x4000a360,430),(0x4018aa40,420),(0x40189354,240)]:
 print('\nWINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
