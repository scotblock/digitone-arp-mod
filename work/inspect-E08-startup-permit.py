from pathlib import Path
import json,sys
c=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text())
for x in c['components']:
 if isinstance(x.get('layout'),dict):print(x['name'],x['layout'])
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
b=Path('work/os144/E07-PC-payload.bin').read_bytes();m=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
for a,z in [(0x47be3b22,0x47be3c50),(0x40095472,0x40095600)]:
 src=b if a>=0x47be0000 else Path('work/os144/E07-PC-main.bin').read_bytes();base=0x47be0000 if a>=0x47be0000 else 0x40000400
 print('WINDOW',hex(a))
 for i in m.disasm(src[a-base:z-base],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
