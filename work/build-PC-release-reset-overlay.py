"""Separate PC-only release and cold-only setup guards; no firmware packaging."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
BASE=0x47fa0900;STATE=0x47be2840
ph=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text())['phases']
main=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();parts=[];layout={};hooks=[]
def absop(a,op,value):absolute(a,op,value)
def save(a):a.emit('4feffff848d7000140c02f400004')
def restore(a):a.emit('202f000446c04cd700014fef0008')
def compare(a,address,value):absop(a,'2039',address);a.emit('0c80'+struct.pack('>I',value).hex());a.branch('6600','deny')
def add(name,site,length,phase,ret=None):
 old=main[site-0x40000400:site-0x40000400+length];a=Asm();save(a);compare(a,STATE,phase)
 if ret is not None:
  a.emit('202f0008'+'0c80'+struct.pack('>I',ret).hex());a.branch('6600','deny')
 restore(a)
 if name=='pool_wrapper':a.emit('4878009e48794009c5aa4ef9400ffed0')
 else:a.emit(old.hex());absop(a,'4ef9',site+length)
 a.label('deny');restore(a);a.emit('4e75')
 code=a.done();addr=BASE+sum(map(len,parts));parts.append(code);layout[name]={'address':addr,'size':len(code)}
 hooks.append({'name':name,'site':site,'length':length,'stock':old.hex(),'replacement':'4ef9'+struct.pack('>I',addr).hex()+'4e71'*((length-6)//2)})
for name,site,length in [('note_off',0x400eae0c,10),('sustain_set',0x400f049a,8),('sustain_release',0x400f0580,8)]:add(name,site,length,ph['live'])
# Setup tail calls inherit normal startup's return. Other entries are denied
# before each recovered operation's first write or prologue mutation.
for name,site,length,ret in [('normal_setup',0x4009d0d8,8,0x4008d31e),('setup_body',0x4009c5ae,6,0x4008d31e),('pool_wrapper',0x4009c5a0,10,0x4009c5d8),('pool_initializer',0x400ffed0,6,0x4009c5aa)]:add(name,site,length,ph['initializing'],ret)
# Exit setup has a flags write before tail-call; refuse the whole entry.
addr=BASE+sum(map(len,parts));parts.append(bytes.fromhex('4e75'));layout['test_exit_refuse']={'address':addr,'size':2}
site=0x4009d0ea;hooks.append({'name':'test_exit_refuse','site':site,'length':6,'stock':main[site-0x40000400:site-0x40000400+6].hex(),'replacement':'4ef9'+struct.pack('>I',addr).hex()})
# Parsed command must bypass its own test-flag clear as well as setup.
a=Asm();a.emit('4879401e2da2');absop(a,'4eb9',0x4000594c);absop(a,'4ef9',0x4008cbe6)
addr=BASE+sum(map(len,parts));code=a.done();parts.append(code);layout['command_exit_cleanup']={'address':addr,'size':len(code)}
site=0x4008b88a;hooks.append({'name':'command_exit_cleanup','site':site,'length':6,'stock':main[site-0x40000400:site-0x40000400+6].hex(),'replacement':'4ef9'+struct.pack('>I',addr).hex()})
blob=b''.join(parts);Path('work/os144/PC_ONLY-release-reset-overlay.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-release-reset-overlay.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'layout':layout,'hooks':hooks,'policy':'Releases and sustain run only in LIVE. Retained notes are preserved while closed; reopening LIVE permits stock cleanup. Setup accepted only in INITIALIZING with recovered cold startup call-chain returns. Test exit/command refused; no reset admitted in LIVE.','limits':['Cold phase plus supplied return addresses is not unforgeable boot provenance.','Recovered boundaries only; unknown computed/interior entries remain unaudited.','Refusal is no-op; caller continuation contracts need tests.','Host-loaded placement and physical RAM/cache ownership unverified.']},indent=2));print('Built',len(blob),'PC-only bytes')

