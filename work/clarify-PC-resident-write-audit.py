from pathlib import Path
import json,sys
sys.path.insert(0,'work/emulator-deps')
from capstone import *
p=Path('outputs/Digitone-E04-PC-resident-copier-callers.json');r=json.loads(p.read_text());d=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();base=0x40000400;cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
r['boot_window']=[{'pc':hex(i.address),'bytes':i.bytes.hex(),'instruction':i.mnemonic+' '+i.op_str} for i in cs.disasm(d[0x40000532-base:0x40000554-base],0x40000532)]
r['literal_classification']=[{'address':'0x4000049a','containing_instruction':'CMPA.L #4029c4b0,A2 at 40000498','meaning':'Exclusive end bound of stock SRAM initialization copy; not a call pointer.'},{'address':'0x4000053a','containing_instruction':'JSR 4029c4b0 at 40000538','meaning':'Direct startup call immediate.'}];p.write_text(json.dumps(r,indent=2))
run=json.loads(Path('outputs/Digitone-E04-PC-resident-storage-extended-runtime.json').read_text());run['DMA_scatter_successors_verified']=False;run['DMA_scatter_limit']='Guest register-write observations include partial programming states with ESG set and DLAST=0. These are not proof that a transfer executes those chains; no successor chain exclusion is certified.';Path('outputs/Digitone-E04-PC-resident-storage-extended-runtime.json').write_text(json.dumps(run,indent=2))
