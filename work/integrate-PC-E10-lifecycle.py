"""Separate decompressed lifecycle image. No SYX/container or release."""
from pathlib import Path
import json,struct,hashlib
c=json.loads(Path('work/os144/PC_ONLY-E10-bound-layout.json').read_text());full=json.loads(Path('work/os144/PC_ONLY-E10-bound-full-layout.json').read_text());b=json.loads(Path('work/os144/PC_ONLY-E10-lifecycle.json').read_text())
raw=Path('work/os144/PC_ONLY-E10-lifecycle.bin').read_bytes();payload=bytearray(Path('work/os144/PC_ONLY-E10-bound-payload.bin').read_bytes());main=bytearray(Path('work/os144/PC_ONLY-E10-bound-main.bin').read_bytes());PB=c['base'];MB=0x40000400
assert PB+len(payload)<=b['base'];payload.extend(bytes(b['base']+len(raw)-PB-len(payload)));payload[b['base']-PB:]=raw
regions=[dict(r) for r in c['regions']];data=list(c['data_regions']);hooks=list(c['hooks'])
for h in b['patches']:
 off=h['site']-PB;assert payload[off:off+h['length']].hex()==h['before'];payload[off:off+h['length']]=bytes.fromhex(h['after'])
 r=next(r for r in regions if r['base']==h['site']);data.append(dict(name=r['name']+'_lifecycle_unreachable_tail',base=r['base']+6,bytes=r['bytes']-6));r['bytes']=6
for h in b['main_hooks']:
 off=h['site']-MB;assert main[off:off+h['length']].hex()==h['before'];main[off:off+h['length']]=bytes.fromhex(h['after']);hooks.append(dict(site=h['site'],length=h['length'],original=h['before'],replacement=h['after']))
regions+=b['regions'];data.append(dict(name='E10_lifecycle_metadata',base=b['meta'],bytes=b['meta_bytes']))
assert len(payload)%4==0 and PB+len(payload)<=0x47c00000
main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4);main[0x4029c5b0-MB:]=payload
sha=lambda d:hashlib.sha256(d).hexdigest()
c.update(lifecycle=b,regions=regions,data_regions=data,hooks=hooks,bytes=len(payload),payload_bytes=len(payload),code_bytes=sum(r['bytes'] for r in regions),copy_longwords=len(payload)//4,copy_source_end=0x4029c5b0+len(payload),copy_destination_end=PB+len(payload),main_sha256=sha(main),payload_sha256=sha(payload),limitations=b['limits']+['Direct MAIN PC startup only. No installable container, physical readiness or E10 loader-derived state.'])
Path('work/os144/PC_ONLY-E10-life-main.bin').write_bytes(main);Path('work/os144/PC_ONLY-E10-life-payload.bin').write_bytes(payload);Path('work/os144/PC_ONLY-E10-life-layout.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
components={r['base']:r for r in full['components']};components.update({r['base']:r for r in regions+data});full.update(c);full['components']=list(components.values());Path('work/os144/PC_ONLY-E10-life-full-layout.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
assert sha(Path('outputs/Digitone_OS1.44E09A_M1_SEQUENCE_FIX_PC_ONLY.syx').read_bytes())=='68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c'
print('PC lifecycle payload',len(payload),'bytes; no firmware container.')
