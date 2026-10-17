from pathlib import Path
import sys,json
sys.path.insert(0,'work/emulator-deps')
from capstone import *
m=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
x=json.loads(Path('work/os144/stock-probe-map.json').read_text())
points=[0x400eae0c,0x4009d0d8,0x4009d0ea,0x4009c5ae,0x4008b88a]+[int(x['sites'][k]['new'],16) for k in ['cc_handler','sustain_on','sustain_release']]
for p in points:
 print('\n',hex(p))
 for i in cs.disasm(m[p-0x40000400:p-0x40000400+60],p):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
