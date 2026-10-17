from pathlib import Path
import json,sys
sys.path.insert(0,'work/emulator-deps')
from capstone import *
data=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040);cs.skipdata=True
windows=[]
for a,n,label in [(0x4000a1a6,32,'pattern argument load'),(0x4000a48e,66,'pattern copy and clear'),(0x4001143e,32,'object interior destination'),(0x4002c1d2,44,'retained destination callback'),(0x4002f448,118,'caller-supplied destination plus allocated source'),(0x400921e6,50,'stack destination'),(0x4002f80c,98,'retained callback construction'),(0x4002c240,46,'retained callback clone'),(0x4018ab1a,194,'buffer copy branches'),(0x40189354,154,'buffer allocator'),(0x401461f4,36,'object buffer getter')]:
 windows.append({'label':label,'start':hex(a),'instructions':[{'pc':hex(i.address),'bytes':i.bytes.hex(),'text':i.mnemonic+' '+i.op_str} for i in cs.disasm(data[a-base:a-base+n],a)]})
Path('outputs/Digitone-E04-PC-copy-pointer-static-windows.json').write_text(json.dumps({'PC_only':True,'windows':windows,'limits':['Capstone skip-data entries are unresolved ColdFire words, not decoded semantics; conclusions use the separately decoded pointer loads/calls/stores.','Direct caller census does not exclude computed or interior entries.']},indent=2))
