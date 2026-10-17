"""Native cold initialization and explicit per-pattern RAM save/load APIs.

The bank is NOT part of the native project format. No stock file padding is used.
Callers must supply a verified pattern slot; no UI/queued-context adapter is claimed.
"""
from pathlib import Path
import json,struct
exec(Path('work/build-PC-live-capture.py').read_text().split('parts=[]')[0])
n=json.loads(Path('work/os144/E09A-PC-install-layout.json').read_text())
X=0x47be9000; S=n['state']; B=0x47beba00; BANK=0x47bee000
INIT=B; STORE=B+0x200; LOAD=B+0x500; VALIDATE=B+0x900
parts=[];regions=[]
def op(a,o,v):absolute(a,o,v)
def add(name,at,a,limit):
 code=a.done();assert len(code)<=limit,(name,len(code));parts.append((at,code));regions.append(dict(name=name,base=at,bytes=len(code)))
def done(a):
 a.label('ok');a.emit('7001');a.branch('6000','return');a.label('deny');a.emit('7000')
 a.label('return');a.emit('2f400000');restore(a);a.emit('4e75')
def live(a):
 op(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','deny')
 op(a,'2039',X);a.emit('0c804d535131');a.branch('6600','deny')
def idle(a):
 for field in [8,12,16,280]:op(a,'4ab9',S+field);a.branch('6600','deny')
def defaults(a):
 op(a,'41f9',X);a.emit('7210');a.label('clear_x');a.emit('42985381');a.branch('6600','clear_x')
 # Publish magic last, after all fields have known values.
 for offset,value in [(8,16),(20,0xffff),(24,0x80000080),(0,0x4d535131)]:
  op(a,'203c',value);op(a,'23c0',X+offset)

# Only the inherited cold-success path may reset the bank. LIVE and busy reset
# requests are refused before the first store; do not clear outstanding owners.
a=Asm();save(a);op(a,'2039',0x47be2840);a.emit('0c80434f4c44');a.branch('6600','deny')
op(a,'2039',S);a.emit('0c804d314131');a.branch('6600','deny');idle(a)
op(a,'41f9',BANK);op(a,'223c',128*8);a.label('clear_bank');a.emit('42985381');a.branch('6600','clear_bank')
defaults(a);done(a);add('E10_cold_initialize',INIT,a,0x200)

# validate(record): all bytes are validated before a load mutates live state.
# Schema: magic[4], version, enabled, length, root, scale, reserved,
# mask[2], signed offsets[16], unsigned byte sum[4]. No pointer/cursor is saved.
a=Asm();a.emit('206f000420100c804d533130');a.branch('6600','bad')
for offset,low,high in [(4,1,1),(5,0,1),(6,1,16),(7,0,11),(8,0,35),(9,0,0)]:
 a.emit('70001028'+struct.pack('>H',offset).hex())
 if low:a.emit('0c80'+struct.pack('>I',low).hex());a.branch('6500','bad')
 a.emit('0c80'+struct.pack('>I',high).hex());a.branch('6200','bad')
a.emit('43e8000c720f');a.label('offsets');a.emit('70001019488048c00c80ffffffe8');a.branch('6d00','bad')
a.emit('0c8000000018');a.branch('6e00','bad');a.emit('5381');a.branch('6a00','offsets')
a.emit('2248721b7400');a.label('sum');a.emit('70001019d4805381');a.branch('6a00','sum')
a.emit('b4a8001c');a.branch('6600','bad');a.emit('70014e75');a.label('bad');a.emit('70004e75')
add('E10_validate_pattern_record',VALIDATE,a,0x300)

# save(slot, owner): quiescent snapshot into a 128-slot M1-only bank.
# Scratch record lives on this function's stack; commit follows full validation.
a=Asm();save(a);live(a);idle(a);a.emit('242f0044262f00480c820000007f');a.branch('6200','deny')
a.emit('4a83');a.branch('6700','deny');op(a,'b6b9',X+28);a.branch('6600','deny')
a.emit('28024fefffe0204f')
op(a,'203c',0x4d533130);a.emit('2080117c000100047000');op(a,'2039',X+4);a.emit('11400005')
op(a,'2039',X+8);a.emit('11400006');op(a,'2039',X+24)
a.emit('220002810000007f11410007ee8802800000003f1140000842280009')
op(a,'2039',X+20);a.emit('3140000a');op(a,'43f9',X+32);a.emit('45e8000c720f')
a.label('copy_offsets');a.emit('101914c05381');a.branch('6a00','copy_offsets')
a.emit('2248721b7400');a.label('sum');a.emit('70001019d4805381');a.branch('6a00','sum');a.emit('2142001c')
# Validate untruncated source fields as well as encoded bytes.
for offset,maximum in [(4,1),(8,16),(20,0xffff)]:
 op(a,'2039',X+offset);a.emit('0c80'+struct.pack('>I',maximum).hex());a.branch('6200','staged_bad')
op(a,'2039',X+24);a.emit('220002817fffe000');a.branch('6600','staged_bad');a.emit('4a80');a.branch('6a00','staged_bad')
a.emit('2f02');op(a,'4879',X);a.emit('2f08');op(a,'4eb9',VALIDATE);a.emit('508f241f4a80');a.branch('6700','staged_bad')
op(a,'43f9',BANK);a.emit('eb8cd3c4204f7207');a.label('commit');a.emit('201822c05381');a.branch('6a00','commit')
a.emit('4fef0020');a.branch('6000','ok');a.label('staged_bad');a.emit('4fef0020');a.branch('6000','deny')
done(a);add('E10_save_pattern_RAM',STORE,a,0x300)

# load(slot, new_owner): refuse active/held/arena state. Invalid/missing records
# return zero with no mutation (the caller must explicitly choose defaults).
a=Asm();save(a);live(a);idle(a);a.emit('242f0044262f00480c820000007f');a.branch('6200','deny')
a.emit('0c8340000000');a.branch('6500','deny');a.emit('0c8347ffff5c');a.branch('6200','deny')
op(a,'45f9',BANK);a.emit('eb8ad5c22f0a');op(a,'4eb9',VALIDATE);a.emit('588f4a80');a.branch('6700','deny')
defaults(a);a.emit('7000102a0005');op(a,'23c0',X+4);a.emit('7000102a0006');op(a,'23c0',X+8)
a.emit('7000302a000a');op(a,'23c0',X+20);a.emit('7000102a0008ef887200122a00078081');op(a,'223c',0x80000000);a.emit('8081');op(a,'23c0',X+24)
op(a,'23c3',X+28);a.emit('41ea000c');op(a,'43f9',X+32);a.emit('720f');a.label('copy');a.emit('101812c05381');a.branch('6a00','copy')
done(a);add('E10_load_pattern_RAM',LOAD,a,0x400)

end=max(p+len(d) for p,d in parts);blob=bytearray(end-B)
for p,d in parts:blob[p-B:p-B+len(d)]=d
Path('work/os144/PC_ONLY-E10-step-lifetime.bin').write_bytes(blob)
Path('work/os144/PC_ONLY-E10-step-lifetime.json').write_text(json.dumps(dict(PC_only=True,base=B,bytes=len(blob),state=X,bank=BANK,bank_bytes=4096,pattern_count=128,record_bytes=32,entries=dict(init=INIT,save=STORE,load=LOAD,validate=VALIDATE),regions=regions,native_project_persistence=False,automatic_pattern_binding=False,limits=['Explicit slot/owner APIs only; adapters to actual pattern publication, native save/load and copy/clear are not installed.','The byte sum detects simple corruption, not malicious edits or all multi-byte corruption.','RAM ownership and physical cache/timing for the enlarged region remain unverified.']),indent=2))
print('E10 lifecycle and RAM bank:',sum(r['bytes'] for r in regions),'native code bytes')
