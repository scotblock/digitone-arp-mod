"""Separate input guards and normal startup completion. PC placement only."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
BASE=0x47fa0600;STATE=0x47be2840
phase_cfg=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text());P=phase_cfg['phases']
cold_cfg=json.loads(Path('work/os144/PC_ONLY-cold-admission-overlay.json').read_text())
parts=[];layout={};hooks=[];image=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();load=0x40000400
def add(name,a):
 code=a.done();layout[name]={'address':BASE+sum(map(len,parts)),'size':len(code)};parts.append(code)
def read(a,address):absolute(a,'2039',address)
def compare(a,value):a.emit('0c80'+struct.pack('>I',value).hex())
def small_save(a):a.emit('4feffff848d7000140c02f400004')
def small_restore(a):a.emit('202f000446c04cd700014fef0008')
# Check before any original argument/frame mutation. No note context or gate
# writes on denial. Stock prologue executes exactly once on LIVE pass-through.
for name,site,length in [('packet_guard',0x400eb2d2,8),('cached_selector_guard',0x400eb166,8),('live_producer_guard',0x400eae5c,6)]:
 displaced=image[site-load:site-load+length]
 a=Asm();small_save(a);read(a,STATE);compare(a,P['live']);a.branch('6600','deny');small_restore(a);a.emit(displaced.hex());absolute(a,'4ef9',site+length);a.label('deny');small_restore(a);a.emit('4e75');add(name,a)
 hooks.append({'name':name,'site':site,'length':length,'stock':displaced.hex(),'replacement':'4ef9'+struct.pack('>I',layout[name]['address']).hex()+'4e71'*((length-6)//2)})
# Replace last visible normal startup call. First execute the full original
# worker constructor/start; publish only on return at the observed boot site.
a=Asm();absolute(a,'4eb9',0x40019444)
a.emit('4fefffe848d7030340c02f40001046fc2700')
for reader,value in [('202f0018',0x4008d3fa)]:a.emit(reader);compare(a,value);a.branch('6600','deny')
read(a,STATE);compare(a,P['initializing']);a.branch('6600','deny')
read(a,0x402296f0);a.emit('028000000040');a.branch('6600','deny')
for address,value in [(0x402a0e50,0),(0x40236788,1),(0x41392fa4,1),(0x400002fc,0x4009d120)]:
 read(a,address);compare(a,value);a.branch('6600','deny')
# Optional context validation. Full stock setup returning in normal state is
# required, but a disabled/corrupted optional feature must not suppress stock.
for address,value in [(0x47be1000,0x47bccf04),(0x47be1004,0x534c4332),(0x47be1008,2),(0x47be100c,0xb70),(0x47be1010,1)]:
 read(a,address);compare(a,value);a.branch('6600','disable_feature')
a.branch('6000','publish')
a.label('disable_feature');a.emit('7000');absolute(a,'23c0',0x47be1010);absolute(a,'23c0',0x47be1000)
a.label('publish');a.emit('70012f00');absolute(a,'4eb9',phase_cfg['layout']['complete']['address']);a.emit('588f4a80');a.branch('6700','deny')
a.emit('202f001046c04cd703034fef00184e75')
a.label('deny');absolute(a,'4ef9',cold_cfg['layout']['failure_stop']['address']);add('normal_completion',a)
hooks.append({'name':'normal_completion','site':0x4008d3f4,'length':6,'stock':image[0x4008d3f4-load:0x4008d3fa-load].hex(),'replacement':'4eb9'+struct.pack('>I',layout['normal_completion']['address']).hex()})
blob=b''.join(parts)
Path('work/os144/PC_ONLY-input-live-overlay.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-input-live-overlay.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'layout':layout,'hooks':hooks,'state':STATE,'input_policy':'Only exact LIVE enters packet wrapper, cached selector or live-note producer. Other phases return before stock prologue. D0 and incoming SR are preserved on denial.','completion_policy':'Full original final startup call returns at observed site; normal flags/vector/INITIALIZING required. Optional context mismatch disables PTR/READY then publishes LIVE for stock fallback.','limits':['Host-loaded fixture-only executable placement, not packaged firmware.','Observed normal completion conditions are not universal failure/exception certification.','Native producer gates cover three recovered entry points, not every CC/sustain/sequencer/panel route.','Warm initializer/command refusal and cold replay provenance remain unresolved.','Failure uses earlier proposed masked PC stop, not hardware recovery.','Denial is no-op at recovered input function boundaries; unobserved callers may require additional contracts.']},indent=2))
print('Built separate input/LIVE overlay',len(blob),'bytes')
