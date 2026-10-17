"""PC-only cache-aware slot helper and two raw-copy call-site wrappers."""
import pathlib,json,hashlib
ns={};exec(pathlib.Path('work/build-compact-hook-overlay.py').read_text().split('changes=[]')[0],ns)
Asm=ns['Asm'];BASE=0x47be0000
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
old=pathlib.Path('work/indexed-context-overlay.bin').read_bytes();blob=bytearray(old)
SLOT=BASE+0x940;COPY=BASE+0x9a0
def jsr(v):return '4eb9'+v.to_bytes(4,'big').hex()
a=Asm();a.emit('220004804199da940c8000002400');a.branch('6500','pool')
a.emit('20010480419a304c0c8000000120');a.branch('6400','fail')
a.emit('80fc004848404a40');a.branch('6600','fail');a.emit('4840e588068000000a004e75')
a.label('pool');a.emit('80fc004848404a40');a.branch('6600','fail');a.emit('4840e5884e75')
a.label('fail');a.emit('70ff4e75');slot=a.done();assert len(slot)<=0x60
blob.extend(bytes(SLOT-BASE-len(blob)));blob.extend(slot);blob.extend(bytes(COPY-BASE-len(blob)))
# Duplicate original memcpy arguments, invoke it once, then preserve its
# complete register/CCR result while propagating sidecar metadata.
a=Asm();a.emit('2f2f000c2f2f000c2f2f000c'+jsr(0x400ec23c)+'4fef000c')
a.emit('4fefffc048d77fff40c03f40003c')
a.emit('2f2f0048'+jsr(layout['snapshot']['address'])+'588f2f002f2f0048'+jsr(layout['candidate_store']['address'])+'508f')
a.emit('302f003c46c04cd77fff4fef00404e75');copy=a.done();blob.extend(copy)
FIRST=BASE+len(blob)
blob.extend(bytes.fromhex('4879')+(FIRST+12).to_bytes(4,'big')+bytes.fromhex('4ef9')+COPY.to_bytes(4,'big'))
blob.extend(bytes.fromhex('4fef000c4ef9')+(0x40093454).to_bytes(4,'big'))
blob.extend(bytes((-len(blob))%4));assert len(blob)<0x1000
# Keep original call interfaces; snapshot/store now recognize exactly four
# additional cache slots, using the already allocated sequencer sidecar.
blob[0x1aa:0x1b0]=bytes.fromhex('4ef9')+SLOT.to_bytes(4,'big')
pathlib.Path('work/cache-context-overlay.bin').write_bytes(blob)
info={'firmware_modified':False,'base':BASE,'slot_address':SLOT,'copy_address':COPY,'first_copy_address':FIRST,'size':len(blob),'slot_size':len(slot),'copy_size':len(copy),'sha256':hashlib.sha256(blob).hexdigest(),'hooks':[0x4009344e,0x40093892],'new_state':False,'sequencer_context_offset':2592,'PC_only_runtime_extension':True}
pathlib.Path('work/cache-context-build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
