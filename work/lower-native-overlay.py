"""Lower unsupported memory CMPI.L; relocate all intra-blob control flow."""
import sys,pathlib,json
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_040)
base=0x47be0000;original=pathlib.Path('work/native-overlay-code.bin').read_bytes()
items=list(md.disasm(original,base));assert sum(i.size for i in items)==len(original)
mapping={};parts=[];offset=0;lowered=[]
for i in items:
 mapping[i.address]=base+offset;data=bytes(i.bytes);op=int.from_bytes(data[:2],'big')
 if op&0xffc0==0x0c80 and op&0x38:
  ea=op&63;ext=bytearray(data[6:])
  if ea==0x2f:ext[:2]=(int.from_bytes(ext[:2],'big',signed=True)+4).to_bytes(2,'big',signed=True)
  data=bytes.fromhex('4feffffc48d70001')+(0x2000|ea).to_bytes(2,'big')+ext+bytes.fromhex('0c80')+data[2:6]+bytes.fromhex('4cd700014fef0004')
  lowered.append(hex(i.address))
 parts.append([i,data]);offset+=len(data)
mapping[base+len(original)]=base+offset
out=bytearray()
for i,data in parts:
 data=bytearray(data);op=int.from_bytes(i.bytes[:2],'big')
 if op&0xf000==0x6000:
  displacement=int.from_bytes(i.bytes[2:4],'big',signed=True) if op&255==0 else int.from_bytes(i.bytes[1:2],'big',signed=True)
  target=i.address+2+displacement
  if target in mapping:
   delta=mapping[target]-mapping[i.address]-2
   if op&255==0:data[2:4]=delta.to_bytes(2,'big',signed=True)
   else:data[1:2]=delta.to_bytes(1,'big',signed=True)
 for j in range(0,len(data)-3,2):
  value=int.from_bytes(data[j:j+4],'big')
  if value in mapping:data[j:j+4]=mapping[value].to_bytes(4,'big')
 out.extend(data)
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
init_old=base+sum(v['size'] for v in layout.values())
startup={'initializer':mapping[init_old],'trampoline':mapping[base+len(original)-16],'end':base+len(out)}
for value in layout.values():
 old=value['address'];value['address']=mapping[old];value['size']=mapping[old+value['size']]-mapping[old]
assert base+len(out)<0x47be1000
pathlib.Path('work/native-overlay-code.bin').write_bytes(out)
pathlib.Path('work/native-overlay-layout.json').write_text(json.dumps(layout))
pathlib.Path('work/native-overlay-startup.json').write_text(json.dumps(startup,indent=2))
pathlib.Path('work/native-overlay-lowering.json').write_text(json.dumps({'lowered_comparisons':lowered,'original_bytes':len(original),'native_bytes':len(out)},indent=2))
print('Lowered',len(lowered),'memory comparisons;',len(out),'bytes',flush=True)
