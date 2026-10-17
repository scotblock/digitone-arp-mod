"""Read-only instruction/absolute-reference inventory; no Capstone/Unicorn needed."""
from pathlib import Path
import sys,struct,json
sys.path.insert(0,'work/upstream/digiemu')
from emu.cfisa import decode
d=Path('work/os144/section-3.bin').read_bytes();base=0x40000400
windows=[]
for start,end in [(0x40003a1e,0x40003a38),(0x400044ec,0x4000463e),(0x40004640,0x4000499c),(0x40005bfc,0x40005c50),(0x40005e04,0x40005eee)]:
 a=start;lines=[]
 while a<end:
  i=decode(lambda r:struct.unpack_from('>H',d,a-base+r)[0],a)
  lines.append({'address':hex(a),'bytes':d[a-base:a-base+i.length].hex(),'operation_class':i.op,'target':hex(i.target) if isinstance(i.target,int) else None});a+=i.length
 windows.append({'start':hex(start),'end':hex(end),'instructions':lines})
refs={}
for value in [0x40529258,0x40529250,0x40529230,0x4000465a,0x4000472a,0x40004806,0x40005e42,0x40005e04]:
 needle=struct.pack('>I',value);at=0;hits=[]
 while True:
  at=d.find(needle,at)
  if at<0:break
  hits.append(hex(base+at));at+=1
 refs[hex(value)]=hits
checks=[]
for a,target in [(0x4000474e,0x4000465a),(0x400047de,0x4000465a),(0x40004996,0x4000465a)]:
 i=decode(lambda r:struct.unpack_from('>H',d,a-base+r)[0],a);assert i.target==target
 checks.append({'branch':hex(a),'replenish_target':hex(target)})
for a,raw in [(0x40004732,'53b940529258'),(0x40004744,'4eb940001424'),(0x40004870,'42b940529258'),(0x40005ed4,'4e92')]:
 assert d[a-base:a-base+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
 checks.append({'address':hex(a),'expected_encoding':raw})
Path('outputs/Digitone-OS1.44E03-USB-producer-static-inventory.json').write_text(json.dumps({'PC_only':True,'execution_tests':False,'static_encoding_checks':checks,'reference_limit':'Literal byte matches, not proof of complete pointer aliases or call graph.','windows':windows,'literal_word_locations':refs},indent=2))
for k,v in refs.items():print(k,v)
