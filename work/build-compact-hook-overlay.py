"""Compact isolated PC helper bodies; retain every validation and entry address."""
import pathlib,sys,json,hashlib
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
BASE=0x47be0000
old=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes();blob=bytearray(old)
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
class Asm:
 def __init__(self):self.ops=[]
 def emit(self,h):self.ops.append(('data',bytes.fromhex(h)))
 def label(self,n):self.ops.append(('label',n))
 def branch(self,op,n):self.ops.append(('branch',int(op[:2],16),n))
 def done(self):
  widths={i:4 for i,v in enumerate(self.ops) if v[0]=='branch'}
  for _ in range(20):
   labels={};positions={};p=0
   for i,v in enumerate(self.ops):
    positions[i]=p
    if v[0]=='label':labels[v[1]]=p
    else:p+=len(v[1]) if v[0]=='data' else widths[i]
   changes=False
   for i,w in widths.items():
    delta=labels[self.ops[i][2]]-positions[i]-2
    if w==4 and -128<=delta<=127 and delta!=0:widths[i]=2;changes=True
   if not changes:break
  result=bytearray()
  for i,v in enumerate(self.ops):
   if v[0]=='data':result.extend(v[1])
   elif v[0]=='branch':
    delta=labels[v[2]]-positions[i]-2;result.append(v[1])
    if widths[i]==2:assert -128<=delta<=127 and delta!=0;result.extend(delta.to_bytes(1,'big',signed=True))
    else:result.append(0);result.extend(delta.to_bytes(2,'big',signed=True))
  return bytes(result)
def resolve():
 a=Asm();a.emit('0c8000000004');a.branch('6400','fail');a.emit('207947be10004a88');a.branch('6700','fail')
 a.emit('2248d3fc000141004feffffc48d70001')
 for op,expected in [('2011',0x534c4332),('20290004',2),('20290008',0xb70),('2029000c',1)]:
  a.emit(op+'0c80'+expected.to_bytes(4,'big').hex());a.branch('6600','savedfail')
 a.emit('4cd700014fef0004e988d1fc00014c30d1c04e75')
 a.label('savedfail');a.emit('4cd700014fef0004');a.label('fail');a.emit('91c84e75')
 return a.done()
md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
def shrink(name):
 site=layout[name];code=old[site['address']-BASE:site['address']-BASE+site['size']]
 items=list(md.disasm(code,site['address']));a=Asm();i=0
 while i<len(items):
  inst=items[i];a.label(inst.address)
  # Pitch D0 is scratch here: the compared value replaces it immediately
  # on both success continuations. Remove two unnecessary save/restore pairs.
  if name=='pitch' and bytes(inst.bytes)==bytes.fromhex('4feffffc'):
   block=items[i:i+6]
   assert len(block)==6 and bytes(block[1].bytes)==bytes.fromhex('48d70001') and bytes(block[4].bytes)==bytes.fromhex('4cd70001') and bytes(block[5].bytes)==bytes.fromhex('4fef0004')
   a.emit(bytes(block[2].bytes).hex()+bytes(block[3].bytes).hex());i+=6;continue
  op=int.from_bytes(inst.bytes[:2],'big')
  if op&0xf000==0x6000:
   delta=int.from_bytes(inst.bytes[2:4],'big',signed=True) if op&255==0 else int.from_bytes(inst.bytes[1:2],'big',signed=True)
   target=inst.address+2+delta;assert site['address']<=target<site['address']+site['size']
   a.branch(bytes(inst.bytes[:1]).hex()+'00',target)
  else:a.emit(bytes(inst.bytes).hex())
  i+=1
 return a.done()
changes=[]
for name,code in [('resolve',resolve()),('read',shrink('read')),('pitch',shrink('pitch'))]:
 site=layout[name];assert len(code)<=site['size'];off=site['address']-BASE
 blob[off:off+site['size']]=code+bytes.fromhex('4e71')*((site['size']-len(code))//2)
 changes.append({'helper':name,'address':hex(site['address']),'previous_bytes':site['size'],'compact_bytes':len(code)})
assert blob[1904:]==old[1904:] and len(blob)==len(old)
pathlib.Path('work/compact-hook-overlay.bin').write_bytes(blob)
info={'firmware_modified':False,'helper_bytes':len(blob),'old_sha256':hashlib.sha256(old).hexdigest(),'sha256':hashlib.sha256(blob).hexdigest(),'table_unchanged':True,'entry_addresses_unchanged':True,'changes':changes,'preserved_checks':['track bounds','pointer validity','header magic/version/size/readiness','event and cached-event type/state/track/identity/flags','selected identity and ownership','retained-context cookie and busy state','quantizer context and pitch bounds']}
pathlib.Path('work/compact-hook-build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
