from pathlib import Path
import sys,json
sys.path.insert(0,'work/emulator-deps')
from capstone import Cs, CS_ARCH_M68K, CS_MODE_M68K_040
base=0x40000400
stock=Path('work/os144/section-3.bin').read_bytes()
mod=Path('work/os144/emulator-E04-main.bin').read_bytes()
cs=Cs(CS_ARCH_M68K,CS_MODE_M68K_040)
out={'ranges':{},'raw_reference_candidates':{}}
for lo,hi in [(0x400fbc58,0x400fbd30),(0x4000185e,0x400019e4),(0x400017dc,0x4000185e),(0x4029c4b0,0x4029c510),(0x40000524,0x40000574)]:
 src=mod if lo==0x4029c4b0 else stock
 rows=[{'pc':hex(i.address),'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operand':i.op_str} for i in cs.disasm(src[lo-base:hi-base],lo)]
 out['ranges'][hex(lo)]={'end':hex(hi),'unchanged_in_E04':stock[lo-base:hi-base]==mod[lo-base:hi-base],'instructions':rows}
 print(hex(lo), 'UNCHANGED',out['ranges'][hex(lo)]['unchanged_in_E04'])
 print('\n'.join(f"{r['pc']} {r['mnemonic']} {r['operand']}" for r in rows))
for target in [0x419eaeec,0x400fbc58,0x40000184,0xfc074000,0xfc074004]:
 needle=target.to_bytes(4,'big');hits=[];pos=0
 while (pos:=stock.find(needle,pos))>=0:
  hits.append(hex(base+pos));pos+=1
 out['raw_reference_candidates'][hex(target)]=hits
 print('literal candidates',hex(target),hits)
Path('outputs/Digitone-E04-completion-code-audit.json').write_text(json.dumps(out,indent=2)+'\n')
