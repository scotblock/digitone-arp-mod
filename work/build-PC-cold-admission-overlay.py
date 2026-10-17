"""Host-loaded PC bootstrap experiment. No existing image/container edits."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
BASE=0x47fa0300;STATE=0x47be2840
admission=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text())
PHASE=admission['phases'];parts=[];layout={}
def add(name,a):
 code=a.done();layout[name]={'address':BASE+sum(map(len,parts)),'size':len(code)};parts.append(code)
def read(a,address):absolute(a,'2039',address)
def compare(a,value):a.emit('0c80'+struct.pack('>I',value).hex())
def store(a,address,value):a.emit('203c'+struct.pack('>I',value).hex());absolute(a,'23c0',address)
# Explicit proposed cold stop: no return into a caller that ignores failure.
# IRQ exclusion is only modeled, and watchdog/NMI/device recovery not proven.
a=Asm();a.emit('46fc2700');store(a,STATE,PHASE['failed']);a.emit('7000');absolute(a,'23c0',0x47be1010);absolute(a,'23c0',0x47be1000);a.label('park');a.branch('6000','park');add('failure_stop',a)
STOP=layout['failure_stop']['address']
def save_frame(a):a.emit('4fefffe848d7030340c02f40001046fc2700')
def restore_frame(a):a.emit('202f001046c04cd703034fef0018')
def finish_or_stop(a,label):
 a.branch('6000',label);a.label('deny');absolute(a,'4ef9',STOP);a.label(label)
# At original copier tail: source already consumed, header established, before
# displaced vector setup. Exact return/header/state checks are bounded checks,
# NOT fresh-boot provenance certification. Copier replay can recreate zero.
a=Asm();save_frame(a)
a.emit('202f0018');compare(a,0x4000053e);a.branch('6600','deny')
read(a,STATE);a.emit('4a80');a.branch('6600','deny')
for address,value in [(0x47be1000,0x47bccf04),(0x47be1004,0x534c4332),(0x47be1008,2),(0x47be100c,0xb70)]:
 read(a,address);compare(a,value);a.branch('6600','deny')
store(a,STATE,PHASE['cold']);finish_or_stop(a,'restore');restore_frame(a);absolute(a,'4ef9',0x40001df4);add('seed_after_copy',a)
# Called only at startup's normal setup call site. Consume before flags/pools.
a=Asm();save_frame(a);a.emit('202f0018');compare(a,0x4008d31e);a.branch('6600','deny')
read(a,0x402296f0);a.emit('028000000040');a.branch('6600','deny')
absolute(a,'4eb9',admission['layout']['claim_cold']['address']);a.emit('4a80');a.branch('6700','deny')
finish_or_stop(a,'restore');restore_frame(a);absolute(a,'4ef9',0x4009d0d8);add('normal_setup_claim',a)
# Diagnostic startup is outside V1 admission. Do not call either diagnostic
# setup function or leave a pending COLD permit. No graceful UI fallback claim.
a=Asm();absolute(a,'4ef9',STOP);add('diagnostic_reject',a)
blob=b''.join(parts);image=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();base=0x40000400
hooks=[]
for name,site,op in [('seed_after_copy',0x4029c518,'4ef9'),('normal_setup_claim',0x4008d318,'4eb9'),('diagnostic_reject',0x4008d326,'4eb9')]:
 hooks.append({'name':name,'site':site,'length':6,'stock':image[site-base:site-base+6].hex(),'replacement':op+struct.pack('>I',layout[name]['address']).hex()})
Path('work/os144/PC_ONLY-cold-admission-overlay.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-cold-admission-overlay.json').write_text(json.dumps({'PC_only':True,'base':BASE,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'layout':layout,'hooks':hooks,'state':STATE,'seeded_by_guest':True,'claim_by_guest':True,'failure':'Proposed interrupt-masked self-loop, not a verified stock graceful abort or hardware recovery.','limitations':['Code is host-loaded at fixture-only RAM; loader/copy/cache delivery is not integrated.','Return/header/zero checks do not exclude computed startup replay.','No completion-to-LIVE or actual producer gate integration.','Failure can freeze the modeled core; watchdog/NMI/peripheral effects and recovery remain unknown.','No firmware or existing raw candidate changed.']},indent=2))
print('Built PC-only cold admission overlay',len(blob),'bytes')
