"""Separate RAM overlay only. No firmware container or existing payload edits."""
from pathlib import Path
import json,struct
BASE=0x47be3000;STATE=0x47be2000;PENDING=STATE+2048
class Asm:
 def __init__(self):self.code=bytearray();self.labels={};self.fix=[]
 def emit(self,h):self.code.extend(bytes.fromhex(h))
 def label(self,n):self.labels[n]=len(self.code)
 def branch(self,op,n):self.emit(op+'0000');self.fix.append((len(self.code)-2,n))
 def done(self):
  for p,n in self.fix:self.code[p:p+2]=struct.pack('>h',self.labels[n]-p)
  return bytes(self.code)
def absolute(a,op,v):a.emit(op+struct.pack('>I',v).hex())
def save(a):a.emit('4fefffc048d77fff40c03f40003c46fc2700')
def restore(a):a.emit('302f003c46c04cd77fff4fef0040')
parts=[];layout={}
def add(n,a):
 code=a.done();layout[n]={'address':BASE+sum(map(len,parts)),'size':len(code)};parts.append(code)
# Map exactly the 128 descriptors of each synth track, excluding stride gaps.
a=Asm();a.emit('0480432203487200');a.label('track');a.emit('0c8000002400');a.branch('6500','within');a.emit('048000002a1852810c8100000004');a.branch('6500','track');a.branch('6000','bad')
a.label('within');a.emit('80fc004848404a40');a.branch('6600','bad');a.emit('484002800000ffffef89d081e5884e75');a.label('bad');a.emit('70ff4e75');add('descriptor_slot',a)
# Hook after the stock input record's 48-byte zero initialization. A2 is still
# its receiving-pattern base, D2 is track, D3 is original (unquantized) note.
a=Asm();save(a);a.emit('202f00080c8000000004');a.branch('6400','end');a.emit('202f000c0c8000000080');a.branch('6400','end');a.emit('202f0008');absolute(a,'4eb9',0x47be0114);a.emit('4a88');a.branch('6700','end')
a.emit('2f2f00082f0a');absolute(a,'4eb9',0x47be0274);a.emit('508f222f0008e789');absolute(a,'41f9',PENDING);a.emit('d1c121400004220e0681ffffffd02081');a.label('end');restore(a);a.emit('2d42ffd02d43ffd4');absolute(a,'4ef9',0x400eaf50);add('noteon_capture',a)
# Bind after the stock producer populated its fields. Pending records are keyed
# by input-record address and consumed once; note-off retains descriptor context.
a=Asm();save(a);a.emit('7000');absolute(a,'4eb9',0x47be0114);a.emit('4a88');a.branch('6700','end');a.emit('202a000c0c8000000001');a.branch('6600','end');a.emit('200c');absolute(a,'4eb9',layout['descriptor_slot']['address']);a.emit('4a80');a.branch('6b00','end');a.emit('2400');absolute(a,'41f9',STATE);a.emit('d1c2429020120c8000000004');a.branch('6400','end');a.emit('e788');absolute(a,'43f9',PENDING);a.emit('d3c0b5d1');a.branch('6600','end');a.emit('20290004429142a900042080');a.label('end');restore(a);a.emit('2940003442ac0044');absolute(a,'4ef9',0x400ff484);add('descriptor_bind',a)
# All three creator copies use this wrapper, including indirect cached replay.
# Execute stock memcpy before saving its returned register/condition state.
a=Asm();a.emit('2f2f000c2f2f000c2f2f000c');absolute(a,'4eb9',0x400fbad8);a.emit('4fef000c');save(a)
a.emit('202f004c0c8000000048');a.branch('6600','end');a.emit('7000');absolute(a,'4eb9',0x47be0114);a.emit('4a88');a.branch('6700','end');a.emit('202f0048');absolute(a,'4eb9',layout['descriptor_slot']['address']);a.emit('4a80');a.branch('6b00','none');absolute(a,'41f9',STATE);a.emit('d1c02010');a.branch('6000','store');a.label('none');a.emit('7000');a.label('store');a.emit('2f002f2f0048');absolute(a,'4eb9',0x47be02ec);a.emit('508f');a.label('end');restore(a);a.emit('4e75');add('live_copy',a)
blob=b''.join(parts)
hooks=[{'site':0x400eaf48,'name':'noteon_capture','op':'4ef9','length':8}, {'site':0x400ff47c,'name':'descriptor_bind','op':'4ef9','length':8}, {'site':0x400ff5f6,'name':'live_copy','op':'4eb9','length':6}, {'site':0x400ff5a6,'name':'live_copy','op':'4bf9','length':6}]
stock=Path('work/os144/section-3.bin').read_bytes()
for h in hooks:h['stock']=stock[h['site']-0x40000400:h['site']-0x40000400+h['length']].hex();h['replacement']=h['op']+struct.pack('>I',layout[h['name']]['address']).hex()+'4e71'*((h['length']-6)//2)
Path('work/os144/PC_ONLY-live-capture-code.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-live-capture-layout.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'state':STATE,'state_bytes':2080,'pending':PENDING,'layout':layout,'hooks':hooks,'initialization':'Host initializes additional descriptor sidecar and pending input records when installing disposable PC overlay; no startup copier modification.','limitation':'Physical ownership and hardware cache handoff of added region unverified.'},indent=2))
print('PC-only live capture:',len(blob),'code bytes; 2080 sidecar/pending bytes')

