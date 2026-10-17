"""PC-only bounded slot lookup: retain header and event ownership checks."""
import pathlib,json,hashlib
exec(pathlib.Path('work/build-compact-hook-overlay.py').read_text().split('changes=[]')[0])
old=pathlib.Path('work/compact-hook-overlay.bin').read_bytes();blob=bytearray(old)
SLOT=0x47be01aa
def calladdr(a):return '4eb9'+a.to_bytes(4,'big').hex()
def slot():
 a=Asm();a.emit('04804199da940c8000002400');a.branch('6400','fail')
 # Offset < 9216 guarantees the 16-bit quotient is < 128, so DIVU.W
 # cannot overflow. The remainder check rejects every non-slot address.
 a.emit('80fc004848404a40');a.branch('6600','fail');a.emit('4840e5884e75')
 a.label('fail');a.emit('70ff4e75');return a.done()
def snapshot():
 a=Asm();a.emit('202f0004'+calladdr(SLOT)+'4a80');a.branch('6b00','fail')
 a.emit('207947be1000d1fc00014120d1c020104e75');a.label('fail');a.emit('42804e75');return a.done()
def store():
 a=Asm();a.emit('7000'+calladdr(layout['resolve']['address'])+'4a88');a.branch('6700','end')
 a.emit('202f0004'+calladdr(SLOT)+'4a80');a.branch('6b00','end')
 a.emit('d1fcfffff4f0d1c0202f00082080');a.label('end');a.emit('4e75');return a.done()
changes=[]
for name,address,size,code in [('slot_offset',SLOT,54,slot()),('snapshot',layout['snapshot']['address'],layout['snapshot']['size'],snapshot()),('candidate_store',layout['candidate_store']['address'],layout['candidate_store']['size'],store())]:
 assert len(code)<=size and len(code)%2==0
 offset=address-BASE;blob[offset:offset+size]=code+bytes.fromhex('4e71')*((size-len(code))//2)
 changes.append({'helper':name,'address':hex(address),'reserved_bytes':size,'body_bytes':len(code)})
assert len(blob)==2324 and blob[1904:]==old[1904:]
pathlib.Path('work/indexed-context-overlay.bin').write_bytes(blob)
info={'firmware_modified':False,'helper_bytes':len(blob),'old_sha256':hashlib.sha256(old).hexdigest(),'sha256':hashlib.sha256(blob).hexdigest(),'table_unchanged':True,'entry_addresses_unchanged':True,'changes':changes,'slot_offset_address':SLOT,'state_added':False,'preserved_checks':['full header magic/version/size/readiness before store','event-pool bounds','exact 72-byte slot alignment','all prior pitch/context ownership checks']}
pathlib.Path('work/indexed-context-build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
