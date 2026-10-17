"""Native project-record capture/emission; separate PC-only overlay."""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text(encoding='utf-8').split('parts=[]')[0])
life=json.loads(Path('work/os144/PC_ONLY-E10-step-lifetime.json').read_text())
S=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text())['state'];X=life['state'];BANK=life['bank'];VALIDATE=life['entries']['validate']
B=0x47bf0000;CAP=B;EMIT=B+0x400;LOAD_HOOK=B+0x800;SAVE_HOOK=B+0xa00;META=B+0x1000
parts=[];regions=[]
def op(a,o,v):absolute(a,o,v)
def add(name,p,a,limit):
 raw=a.done();assert len(raw)<=limit,(name,len(raw));parts.append((p,raw));regions.append(dict(name=name,base=p,bytes=len(raw)))
def finish(a):
 a.label('ok');a.emit('7001');a.branch('6000','return');a.label('deny');a.emit('7000');a.label('return');a.emit('2f400000');restore(a);a.emit('4e75')
def span(a):
 # Serialized argument A2 covers the complete current-version project image.
 a.emit('200a0c8040000000');a.branch('6500','deny');a.emit('0c8047d58bfc');a.branch('6200','deny')
def record_copy(a,label):
 a.emit('7207');a.label(label);a.emit('201822c05381');a.branch('6a00',label)
def record_zero(a,label):
 a.emit('7207');a.label(label);a.emit('42995381');a.branch('6a00',label)

# capture(serialized_project, runtime_project): called only after the actual
# project decoder's complete kit loop and current-version header checks.
# Failure invalidates ownership; the old bank is never reused as this project.
a=Asm();save(a);a.emit('246f0044262f0048');op(a,'42b9',META+4);span(a)
a.emit('0c8340000000');a.branch('6500','refuse');a.emit('0c8347494000');a.branch('6200','refuse')
op(a,'2039',X);a.emit('0c804d535131');a.branch('6600','refuse')
op(a,'2039',0x47be2840);a.emit('0c80434f4c44');a.branch('6700','admitted');a.emit('0c804c495645');a.branch('6600','refuse')
a.label('admitted')
for offset in [8,12,16,280]:op(a,'4ab9',S+offset);a.branch('6600','refuse')
a.emit('47ea0000d7fc00240b40');op(a,'49f9',BANK);a.emit('7a007c7f')
a.label('records');a.emit('2f0b');op(a,'4eb9',VALIDATE);a.emit('588f224c4a80');a.branch('6700','invalid')
a.emit('204b');record_copy(a,'capture_copy');a.emit('5285');a.branch('6000','next')
a.label('invalid');record_zero(a,'capture_zero')
a.label('next');a.emit('49ec002047eb0a005386');a.branch('6a00','records')
op(a,'203c',0x4d535031);op(a,'23c0',META);op(a,'23c3',META+8);op(a,'52b9',META+12);op(a,'23c5',META+16)
a.emit('7001');op(a,'23c0',META+4);a.branch('6000','ok')
a.label('refuse');op(a,'52b9',META+20);a.branch('6000','deny');finish(a);add('E10_capture_project_records',CAP,a,0x400)

# emit(serialized_project, runtime_project): only the captured project may
# supply records. Otherwise write explicit zeros, including reused buffers.
# The bank is a stable snapshot independent of the current held-note state.
a=Asm();save(a);a.emit('246f0044262f0048');span(a);a.emit('7a00')
op(a,'2039',META);a.emit('0c804d535031');a.branch('6600','unowned');op(a,'4ab9',META+4);a.branch('6700','unowned');op(a,'b6b9',META+8);a.branch('6600','unowned')
a.emit('7a01');a.branch('6000','start');a.label('unowned');op(a,'52b9',META+28)
a.label('start');a.emit('47ea0000d7fc00240b40');op(a,'49f9',BANK);a.emit('7c7f7e00')
a.label('records');a.emit('4a85');a.branch('6700','invalid');a.emit('2f0c');op(a,'4eb9',VALIDATE);a.emit('588f4a80');a.branch('6700','invalid')
a.emit('204c224b');record_copy(a,'emit_copy');a.emit('5287');a.branch('6000','next')
a.label('invalid');a.emit('224b');record_zero(a,'emit_zero')
a.label('next');a.emit('49ec002047eb0a005386');a.branch('6a00','records')
op(a,'23c7',META+24);a.emit('4a85');a.branch('6700','deny');finish(a);add('E10_emit_project_records',EMIT,a,0x400)

# Native project decode has A3=image/A4=runtime at the kit-loop completion.
# Replay the overwritten progress branch, preserving all registers and flags.
a=Asm();save(a);a.emit('2f0c2f0b');op(a,'4eb9',CAP);a.emit('508f');restore(a)
a.emit('4aaa0008');a.branch('6700','skip');a.emit('4878000c');op(a,'4ef9',0x4000e994)
a.label('skip');op(a,'4ef9',0x4000e9a8);add('E10_native_project_decode_hook',LOAD_HOOK,a,0x200)
# Emit before the stock kit loop: its verified occupied extent ends at +0x90e.
a=Asm();save(a);a.emit('2f032f0b');op(a,'4eb9',EMIT);a.emit('508f');restore(a);a.emit('287c00240200');op(a,'4ef9',0x4000ecc6);add('E10_native_project_encode_hook',SAVE_HOOK,a,0x200)

stock=Path('work/os144/section-3.bin').read_bytes();hooks=[]
for site,target,length,expected in [(0x4000e98a,LOAD_HOOK,10,'4aaa000867184878000c'),(0x4000ecc0,SAVE_HOOK,6,'287c00240200')]:
 before=stock[site-0x40000400:site-0x40000400+length];assert before.hex()==expected
 hooks.append(dict(site=site,length=length,before=before.hex(),after='4ef9'+struct.pack('>I',target).hex()+'4e71'*((length-6)//2)))
blob=bytearray(META+32-B)
for p,raw in parts:blob[p-B:p-B+len(raw)]=raw
Path('work/os144/PC_ONLY-E10-persistence-bridge.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-E10-persistence-bridge.json').write_text(json.dumps(dict(PC_only=True,base=B,bytes=len(blob),regions=regions,hooks=hooks,meta=META,bank=BANK,entries=dict(capture=CAP,emit=EMIT),meta_fields=dict(magic=0,valid=4,owner=8,generation=12,captured=16,refusals=20,emitted=24,mismatches=28),limits=['PC-only native persistence bridge. Editor-to-pattern binding and runtime pattern recall are separate.','Capture is quiescent-only; refusal invalidates bank ownership but does not certify outer project replacement or change active notes.','Full interrupt masking bounds atomic helper publication; physical cost/ownership of the expanded region is not certified.']),indent=2))
print('Native persistence bridge:',sum(r['bytes'] for r in regions),'code bytes')
