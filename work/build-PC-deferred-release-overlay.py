"""PC-only bounded deferred releases; fixture RAM, explicit resume API."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
BASE=0x47fa0c00;STATE=0x47be2840;COUNT=0x47fa2000;ERROR=COUNT+4;DRAIN=COUNT+8;ENTRIES=COUNT+16;CAP=32
parts=[];layout={};main=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();previous=json.loads(Path('work/os144/PC_ONLY-release-reset-overlay.json').read_text())
def add(name,a):
 c=a.done();addr=BASE+sum(map(len,parts));parts.append(c);layout[name]={'address':addr,'size':len(c)};return addr
def read(a,addr):absolute(a,'2039',addr)
def cmp(a,v):a.emit('0c80'+struct.pack('>I',v).hex())
def save(a):a.emit('4fefffe848d7030740c02f40001446fc2700')
def restore(a):a.emit('202f001446c04cd703074fef0018')
def ret(a,value=None):
 if value is not None:a.emit('700'+str(value)+'2f400000')
 restore(a);a.emit('4e75')
# Original entry replay; subsequent body remains at its original addresses.
a=Asm();a.emit(main[0x400eabb4-0x40000400:0x400eabba-0x40000400].hex());absolute(a,'4ef9',0x400eabba);tramp=add('stock_internal_release',a)
a=Asm();save(a);read(a,STATE);cmp(a,0x4c495645);a.branch('6700','stock');cmp(a,0x494e4954);a.branch('6600','deny');read(a,DRAIN);cmp(a,0);a.branch('6600','overflow')
# Stack arguments, before original prologue, with saved scratch frame 24.
a.emit('202f001c');cmp(a,7);a.branch('6200','deny');a.emit('202f0020');cmp(a,127);a.branch('6200','deny')
# Use the stock per-track/per-pitch reference count to distinguish repeated
# valid releases from duplicate messages. Zero references permits one stock
# cleanup attempt; no synthetic note-owner claim is made.
a.emit('202f001cef88d0af0020e5880680419952a8224020114a80');a.branch('6e00','budget');a.emit('7001');a.label('budget');a.emit('2240')
read(a,COUNT);cmp(a,CAP);a.branch('6200','overflow');a.emit('2400720041f9'+struct.pack('>I',ENTRIES).hex())
a.label('scan');a.emit('4a82');a.branch('6700','append')
for reader,comparison in [('202f001c','b090'),('202f0020','b0a80004')]:a.emit(reader+comparison);a.branch('6600','next')
a.emit('5281');a.label('next');a.emit('41e8000c5382');a.branch('6000','scan')
a.label('append');a.emit('2009b081');a.branch('6300','deny');read(a,COUNT);cmp(a,CAP);a.branch('6400','overflow')
for reader,store in [('202f001c','2080'),('202f0020','21400004'),('202f0024','21400008')]:a.emit(reader+store)
read(a,COUNT);a.emit('5280');absolute(a,'23c0',COUNT);a.branch('6000','deny')
a.label('overflow');a.emit('7001');absolute(a,'23c0',ERROR)
a.label('deny');ret(a)
a.label('stock');restore(a);absolute(a,'4ef9',tramp);internal=add('internal_release_guard',a)
# Boolean helper: refusal always means handled, independent of incoming D0.
a=Asm();save(a);read(a,STATE);cmp(a,0x4c495645);a.branch('6700','stock');cmp(a,0x494e4954);a.branch('6600','deny');read(a,DRAIN);cmp(a,1);a.branch('6600','deny');a.emit('202f0018');cmp(a,0x400eabdc);a.branch('6600','deny');a.emit('202f0014028000000700');cmp(a,0x700);a.branch('6600','deny')
a.label('stock');restore(a);a.emit(main[0x400f0580-0x40000400:0x400f0588-0x40000400].hex());absolute(a,'4ef9',0x400f0588)
a.label('deny');ret(a,1);sustain=add('sustain_handled_guard',a)
# Native resume drains under IPL7 before the final LIVE publication. API
# return 1 means drained/published; 0 leaves admission closed. D2/A2 survive
# native stock release calls. Exceptions deliberately do not publish LIVE.
a=Asm();a.emit('4fefffe048d7070f40c02f40001c46fc2700')
for addr,v in [(STATE,0x494e4954),(ERROR,0),(DRAIN,0)]:read(a,addr);cmp(a,v);a.branch('6600','fail')
read(a,COUNT);cmp(a,CAP);a.branch('6200','fail');a.emit('2400');a.emit('7001');absolute(a,'23c0',DRAIN);a.emit('45f9'+struct.pack('>I',ENTRIES).hex())
a.label('loop');a.emit('4a82');a.branch('6700','finish');a.emit('2f2a00082f2a00042f12');absolute(a,'4eb9',tramp);a.emit('4fef000c45ea000c5382');a.branch('6000','loop')
a.label('finish');read(a,ERROR);cmp(a,0);a.branch('6600','fail');read(a,STATE);cmp(a,0x494e4954);a.branch('6600','fail');a.emit('7000');absolute(a,'23c0',COUNT);absolute(a,'23c0',DRAIN);a.emit('203c4c495645');absolute(a,'23c0',STATE);a.emit('7001');a.branch('6000','return')
a.label('fail');a.emit('7000');a.label('return');a.emit('2f400000202f001c46c04cd7070f4fef00204e75');resume=add('resume_deferred',a)
a=Asm();save(a);a.emit('202f001c');cmp(a,1);a.branch('6600','original');restore(a);absolute(a,'4ef9',resume)
a.label('original');restore(a);a.emit(Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()[68:76].hex());absolute(a,'4ef9',0x47fa004c);dispatch=add('completion_dispatch',a)
blob=b''.join(parts);hooks=[]
for name,site,n,addr in [('internal_release_guard',0x400eabb4,6,internal),('sustain_handled_guard',0x400f0580,8,sustain)]:
 old=next((h['replacement'] for h in previous['hooks'] if h['site']==site),main[site-0x40000400:site-0x40000400+n].hex());hooks.append({'name':name,'site':site,'length':n,'previous':old,'replacement':'4ef9'+struct.pack('>I',addr).hex()+'4e71'*((n-6)//2)})
hooks.append({'name':'completion_dispatch','site':0x47fa0044,'length':8,'previous':Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()[68:76].hex(),'replacement':'4ef9'+struct.pack('>I',dispatch).hex()+'4e71'})
Path('work/os144/PC_ONLY-deferred-release-overlay.bin').write_bytes(blob);Path('work/os144/PC_ONLY-deferred-release-overlay.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'layout':layout,'hooks':hooks,'count':COUNT,'error':ERROR,'drain':DRAIN,'entries':ENTRIES,'capacity':CAP,'storage_bytes':16+CAP*12,'limits':['New RAM is fixture-only and zeroed by test installation, not owned/initialized through a packaged boot path.','Existing native completion success dispatch now drains before LIVE; real warm closure still unimplemented/refused.','Assumes guarded pool ownership persists; no arbitrary warm reset/recycling certification.','Exception during drain remains closed with DRAIN set; rollback and recovery not implemented.','Replay runs stock release code under IPL7; physical latency and interrupt effects unverified.']},indent=2));print('Built PC deferred release',len(blob),'bytes')

