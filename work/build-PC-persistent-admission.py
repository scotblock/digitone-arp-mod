"""Disposable native admission overlay; no startup or firmware integration."""
from pathlib import Path
import json, struct, hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
BASE=0x47fa0000
ADMISSION=0x47be2840
phases={'cold':0x434f4c44,'initializing':0x494e4954,'live':0x4c495645,'failed':0x4641494c}
parts=[];layout={}
def add(name,a):
 code=a.done();layout[name]={'address':BASE+sum(map(len,parts)),'size':len(code)};parts.append(code)
def read(a):absolute(a,'2039',ADMISSION)
def cmp(a,phase):a.emit('0c80'+struct.pack('>I',phases[phase]).hex())
def write(a,phase):a.emit('203c'+struct.pack('>I',phases[phase]).hex());absolute(a,'23c0',ADMISSION)
def enter(a):a.emit('4feffff848d7000240c12f41000446fc2700')
def leave(a):a.emit('222f000446c14cd70002508f4e75')
# No helper seeds COLD. A future trusted cold bootstrap must establish it once.
# Check and consumption execute within one saved/restored interrupt mask.
a=Asm();enter(a);read(a);cmp(a,'cold');a.branch('6600','deny');write(a,'initializing');a.emit('7001');a.branch('6000','end');a.label('deny');a.emit('7000');a.label('end');leave(a);add('claim_cold',a)
# Stock completion/normal-mode success is a fixture argument here, not yet
# derived from a verified native startup continuation. Feature READY is unused.
a=Asm();enter(a);read(a);cmp(a,'initializing');a.branch('6600','deny');a.emit('202f000c0c8000000001');a.branch('6600','fail');write(a,'live');a.branch('6000','ok');a.label('fail');write(a,'failed');a.label('ok');a.emit('7001');a.branch('6000','end');a.label('deny');a.emit('7000');a.label('end');leave(a);add('complete',a)
stock=Path('work/os144/section-3.bin').read_bytes();base=0x40000400;hooks=[]
for name,site,length,load,resume,target in [('retained_defer',0x400e4e42,8,'206a008c',0x400e4e4a,0x400e4eae),('explicit_refuse',0x400e47f6,6,'2052',0x400e47fc,0x400e483c)]:
 a=Asm();a.emit('2f002f08');read(a);cmp(a,'cold');a.branch('6700','stock');a.emit(load+'4a88');a.branch('6700','stock');a.emit('20100c80401c4714');a.branch('6600','stock');a.emit('2028ffc80c80401c467c');a.branch('6600','stock');a.emit('205f201f')
 if name=='explicit_refuse':a.emit('7000')
 absolute(a,'4ef9',target);a.label('stock');a.emit('205f201f');a.emit(stock[site-base:site-base+length].hex());absolute(a,'4ef9',resume);add(name,a)
 hooks.append({'name':name,'site':site,'length':length,'stock':stock[site-base:site-base+length].hex(),'replacement':'4ef9'+struct.pack('>I',layout[name]['address']).hex()+'4e71'*((length-6)//2)})
blob=b''.join(parts)
Path('work/os144/PC_ONLY-persistent-admission.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-persistent-admission.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'state_address':ADMISSION,'state_bytes':4,'phases':phases,'layout':layout,'hooks':hooks,'initialization':'No native cold seed. Tests supply a trusted-cold fixture value. Existing payload has zero here, which denies admission.','storage':'Candidate word outside known reset clears; bounded write tracing required. Physical exclusive ownership remains unproven.','limits':['No startup integration, initializer gate or whole-command guard.','Completion argument is fixture supplied; stock success and mode provenance not integrated.','Interrupt masking serializes on one modeled core, not an actual callback exclusion proof.','Code placement is a disposable fixture; no flashable firmware generated.']},indent=2))
print('Built disposable persistent admission:',len(blob),'bytes')
