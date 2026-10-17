"""Extend the separate decompressed PC image; no firmware container."""
from pathlib import Path
import json,struct,hashlib
c=json.loads(Path('work/os144/PC_ONLY-E10-persistence-layout.json').read_text());full=json.loads(Path('work/os144/PC_ONLY-E10-persistence-full-layout.json').read_text())
b=json.loads(Path('work/os144/PC_ONLY-E10-pattern-binding.json').read_text());raw=Path('work/os144/PC_ONLY-E10-pattern-binding.bin').read_bytes()
payload=bytearray(Path('work/os144/PC_ONLY-E10-persistence-payload.bin').read_bytes());main=bytearray(Path('work/os144/PC_ONLY-E10-persistence-main.bin').read_bytes());PB=c['base'];MB=0x40000400
assert PB+len(payload)<=b['base'];payload.extend(bytes(b['base']+len(raw)-PB-len(payload)));payload[b['base']-PB:]=raw
regions=[dict(r) for r in c['regions']];data=list(c['data_regions'])
for h in b['patches']:
 off=h['site']-PB;assert payload[off:off+6].hex()==h['before'];payload[off:off+6]=bytes.fromhex(h['after'])
 r=next(r for r in regions if r['base']==h['site']);data.append(dict(name=r['name']+'_binding_unreachable_tail',base=r['base']+6,bytes=r['bytes']-6));r['bytes']=6
data.append(dict(name='E10_pattern_binding_metadata',base=b['meta'],bytes=b['meta_bytes']))
regions+=b['regions'];assert len(payload)%4==0 and PB+len(payload)<=0x47c00000
main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4);main[0x4029c5b0-MB:]=payload
sha=lambda d:hashlib.sha256(d).hexdigest()
c.update(regions=regions,data_regions=data,binding=b,bytes=len(payload),payload_bytes=len(payload),code_bytes=sum(r['bytes'] for r in regions),copy_longwords=len(payload)//4,copy_source_end=0x4029c5b0+len(payload),copy_destination_end=PB+len(payload),main_sha256=sha(main),payload_sha256=sha(payload),automatic_pattern_binding=True,editor_to_pattern_bank_connected=True,limitations=b['limits']+['Direct MAIN PC startup only; no E10 firmware container or loader-derived E10 state.'])
Path('work/os144/PC_ONLY-E10-bound-main.bin').write_bytes(main);Path('work/os144/PC_ONLY-E10-bound-payload.bin').write_bytes(payload);Path('work/os144/PC_ONLY-E10-bound-layout.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
components={r['base']:r for r in full['components']};components.update({r['base']:r for r in regions+data})
full.update(c);full['components']=list(components.values());Path('work/os144/PC_ONLY-E10-bound-full-layout.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
assert sha(Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx').read_bytes())=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
print('Bound E10 PC image:',len(payload),'copied bytes; E09A unchanged.')
