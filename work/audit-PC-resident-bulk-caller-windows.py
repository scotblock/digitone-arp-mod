from pathlib import Path
import sys,json
sys.path.insert(0,'work/emulator-deps')
from capstone import *
d=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040);rows=[]
for start,n in [(0x4009bfc0,64),(0x4000a478,78),(0x4000879c,64)]:
 items=[{'pc':hex(i.address),'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str} for i in cs.disasm(d[start-base:start-base+n],start)]
 rows.append({'start':hex(start),'instructions':items});print(hex(start),[(i['pc'],i['instruction']) for i in items])
Path('outputs/Digitone-E04-PC-resident-bulk-caller-windows.json').write_text(json.dumps({'PC_only':True,'windows':rows,'limits':['Decoded caller windows verify sampled fixed lengths and offsets; incoming base-pointer ownership is not globally proven.']},indent=2))
