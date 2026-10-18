"""Separate E11 decompressed startup image; preserve the E10 record format."""
from pathlib import Path
import json,struct,hashlib
folder=Path('work/os144');c=json.loads((folder/'PC_ONLY-E10-package-layout.json').read_text());full=json.loads((folder/'PC_ONLY-E10-package-full-layout.json').read_text());ui=json.loads((folder/'PC_ONLY-E11-synth-style-editor.json').read_text());code=(folder/'PC_ONLY-E11-synth-style-editor.bin').read_bytes()
payload=bytearray((folder/'PC_ONLY-E10-package-payload.bin').read_bytes());main=bytearray((folder/'PC_ONLY-E10-package-main.bin').read_bytes());PB=c['base'];MB=0x40000400
regions=[dict(r) for r in c['regions']];data=list(c['data_regions'])
for patch in ui['patches']:
 off=patch['site']-PB;assert payload[off:off+6].hex()==patch['before'];payload[off:off+6]=bytes.fromhex(patch['after'])
 r=next(r for r in regions if r['base']==patch['site']);data.append(dict(name=r['name']+'_E11_unreachable_tail',base=r['base']+6,bytes=r['bytes']-6));r['bytes']=6
assert ui['base']>=PB+len(payload)
payload.extend(bytes(ui['base']-PB-len(payload)));payload.extend(code);assert len(payload)%4==0 and PB+len(payload)<=0x47c00000
data.append(dict(name='E11_step_grid_strings_tables',base=ui['base']+0xe00,bytes=0x600))
regions+=ui['regions'];main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4);main[0x4029c5b0-MB:]=payload
sha=lambda b:hashlib.sha256(b).hexdigest()
c.update(E11_UI=ui,regions=regions,data_regions=data,bytes=len(payload),payload_bytes=len(payload),copy_longwords=len(payload)//4,copy_source_end=0x4029c5b0+len(payload),copy_destination_end=PB+len(payload),main_sha256=sha(main),payload_sha256=sha(payload),hardware_ready=False,firmware_release_created=False,limitations=['E11 separate PC candidate; E10 playback and record formats retained.','Physical timing/cache, expanded copied-code interval and hardware UI behavior remain unvalidated.'])
# The copier's immediate is itself inside the executable copier region. All
# downstream comparison tables derive expected MAIN bytes from this new image.
(folder/'PC_ONLY-E11-editor-main.bin').write_bytes(main);(folder/'PC_ONLY-E11-editor-payload.bin').write_bytes(payload);(folder/'PC_ONLY-E11-editor-layout.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
components={r['base']:r for r in full['components']};components.update({r['base']:r for r in regions+data});full.update(c);full['components']=list(components.values());(folder/'PC_ONLY-E11-editor-full-layout.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
print('E11 startup image:',len(payload),'copied bytes; unchanged state and record format.')
