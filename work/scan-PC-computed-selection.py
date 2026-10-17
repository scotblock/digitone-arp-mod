from pathlib import Path
import sys,json
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from capstone import *
from emu import cfisa
b=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040);c.skipdata=True
refs={}
for t in [0x400e47e6,0x400e4848,0x40072a7e]:
 rows=[]
 for i in range(0,len(b)-4,2):
  pc=base+i;w=int.from_bytes(b[i:i+2],'big');kind=None
  if b[i:i+6] in [b'\x4e\xb9'+t.to_bytes(4,'big'),b'\x4e\xf9'+t.to_bytes(4,'big')]:kind='absolute call/jump'
  if w in [0x4eba,0x4efa] and pc+2+int.from_bytes(b[i+2:i+4],'big',signed=True)==t:kind='PC relative call/jump'
  if w>>8 in [0x60,0x61]:
   d=w&255
   disp=int.from_bytes(b[i+2:i+4],'big',signed=True) if d==0 else (int.from_bytes(b[i+2:i+6],'big',signed=True) if d==255 else (d if d<128 else d-256))
   if pc+2+disp==t:kind='relative branch/call candidate'
  if kind:rows.append({'pc':hex(pc),'kind':kind})
 literals=[];needle=t.to_bytes(4,'big');pos=b.find(needle)
 while pos>=0:literals.append(hex(base+pos));pos=b.find(needle,pos+1)
 refs[hex(t)]={'calls':rows,'literal_locations':literals}
 print(hex(t),json.dumps(refs[hex(t)]))
 for r in rows:
  lo=int(r['pc'],16)-28;hi=lo+100;print('REGION',hex(lo))
  for ins in c.disasm(b[lo-base:hi-base],lo):print(hex(ins.address),ins.mnemonic,ins.op_str)
Path('outputs/Digitone-E04-PC-computed-selection-refs.json').write_text(json.dumps({'scope':'aligned byte-pattern direct/relative call candidates and all literal occurrences; candidates require instruction-boundary validation; computed targets not exhausted','targets':refs},indent=2))
