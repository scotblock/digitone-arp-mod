from pathlib import Path
import json,sys
sys.path.insert(0,'work/emulator-deps')
from capstone import *
image=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();base=0x40000400;target=0x4029c4b0;rows=[];words=[]
for p in range(0,len(image)-5,2):
 w=int.from_bytes(image[p:p+2],'big')
 if w in [0x4eb9,0x4ef9] and int.from_bytes(image[p+2:p+6],'big')==target:rows.append({'pc':hex(base+p),'kind':'JSR' if w==0x4eb9 else 'JMP'})
 if w in [0x6100,0x6000] and base+p+2+int.from_bytes(image[p+2:p+4],'big',signed=True)==target:rows.append({'pc':hex(base+p),'kind':'relative BSR/BRA candidate'})
 if int.from_bytes(image[p:p+4],'big')==target:words.append(hex(base+p))
cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040);boot=[{'pc':hex(i.address),'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str} for i in cs.disasm(image[0x40000522-base:0x40000558-base],0x40000522)]
r={'PC_only':True,'target':hex(target),'direct_call_candidates':rows,'literal_pointer_candidates':words,'boot_window':boot,'limits':['Aligned literal/opcode screen identifies candidates, not complete reachable control flow.','Computed jumps, interior entries, table construction and reset-vector replay remain unproven.']}
Path('outputs/Digitone-E04-PC-resident-copier-callers.json').write_text(json.dumps(r,indent=2));print(rows,words)
