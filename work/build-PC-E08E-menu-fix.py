"""Correct only menu helpers in a separate PC overlay. No firmware container."""
from pathlib import Path
import json,struct,hashlib
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
cfg=json.loads(Path('work/os144/E08E-PC-install-layout.json').read_text())
old=Path('work/os144/E08E-PC-layout-payload.bin').read_bytes();payload=bytearray(old)
SEL=next(r['base'] for r in cfg['regions'] if r['name']=='selected_track')
def js(a,p):absolute(a,'4eb9',p)
def jump(a,p):absolute(a,'4ef9',p)
def ui_save(a):
    save(a);assert a.code[-4:]==bytes.fromhex('46fc2700');a.code[-4:]=bytes.fromhex('4e714e71')
regions=[]
def add(name,a,limit):
    r=next(r for r in cfg['regions'] if r['name']==name);code=a.done()
    assert len(code)<=limit
    off=r['base']-cfg['base'];size=max(len(code),r['bytes'])
    payload[off:off+size]=code+bytes(size-len(code))
    regions.append({**r,'old_bytes':r['bytes'],'bytes':len(code),'span':size,'before':old[off:off+size].hex(),'after':bytes(payload[off:off+size]).hex()})

a=Asm();ui_save(a)
a.emit('4a2f000f');a.branch('6700','original') # low byte of preserved D3: modifier
a.emit('202f00300c8000000016');a.branch('6600','original')
js(a,SEL);a.emit('0c8000000004');a.branch('6600','original')
restore(a);jump(a,0x4003fc42)
a.label('original');restore(a);a.emit('4a03');a.branch('6600','modified')
a.emit('42a7486cffec');jump(a,0x4003fb92)
a.label('modified');jump(a,0x4003fb9c)
add('M1_SYN2_open',a,256)

a=Asm();ui_save(a)
a.emit('202f00300c8000000016');a.branch('6600','end')
a.emit('4a2f000f');a.branch('6700','end')
js(a,SEL);a.emit('0c8000000004');a.branch('6600','end')
a.emit('206f00084a88');a.branch('6700','end')
a.emit('203c4d314352214002c8')
a.label('end');restore(a);a.emit('2f02240e0682fffffff0');jump(a,0x4003fc60)
add('mark_M1_view',a,128)

report={'PC_only':True,'firmware_container_created':False,'base':cfg['base'],
 'source_payload_sha256':hashlib.sha256(old).hexdigest(),'overlay_payload_sha256':hashlib.sha256(payload).hexdigest(),
 'selected_track':SEL,'regions':regions,'changes':['Stock page subtraction is -20, not -14.','Only M1 FUNC+SYN2 opens custom controls.','Only that same M1 entry marks a custom page.']}
Path('work/os144/PC_ONLY-E08E-menu-fix-payload.bin').write_bytes(payload)
Path('work/os144/PC_ONLY-E08E-menu-fix-layout.json').write_text(json.dumps(report,indent=2))
print('PC-only menu helpers:',[(r['name'],r['bytes']) for r in regions])
