"""Separate native startup-copied routing candidate; E08F preserved."""
from pathlib import Path
import json,hashlib,struct
for f in ['Digitone-E09-PC-dual-port-mirror.json','Digitone-E09-PC-dual-port-ISA.json','Digitone-E09-M1-both-ports.json','Digitone-E09-synth-both-ports.json']:
 assert json.loads(Path('outputs',f).read_text())['passed']
sha=lambda b:hashlib.sha256(b).hexdigest()
full=json.loads(Path('outputs/Digitone-E08F-PC-path-layout.json').read_text())
native=json.loads(Path('work/os144/E08F-PC-install-layout.json').read_text())
dual=json.loads(Path('work/os144/E09-PC-dual-port-layout.json').read_text())
payload=Path('work/os144/E09-PC-dual-port-payload.bin').read_bytes()
main=bytearray(Path('work/os144/E08F-PC-layout-main.bin').read_bytes());MB=0x40000400
assert main[0x4029c4be-MB:0x4029c4c2-MB]==struct.pack('>I',full['copy_longwords'])
assert len(payload)%4==0 and dual['base']+len(payload)<=0x47c00000
main[0x4029c4be-MB:0x4029c4c2-MB]=struct.pack('>I',len(payload)//4)
main[full['copy_source']-MB:]=payload
for cfg in [full,native]:
 cfg['regions']+=dual['regions']
 cfg.update(PC_only=True,hardware_ready=False,parent_build='E08F',bytes=len(payload),payload_bytes=len(payload),copy_longwords=len(payload)//4,
   copy_source_end=cfg['copy_source']+len(payload),copy_destination_end=dual['base']+len(payload),additional_copy_bytes=len(payload)-cfg['old_payload_bytes'],
   main_sha256=sha(main),payload_sha256=sha(payload),USB_mirror_state=dual['USB_state'],USB_mirror_state_bytes=160,USB_mirror_records=dual['USB_records'],
   dual_port_synth_mirroring=True,MIDI_route='Normal output mask: DIN, USB, or both; independent per-port synth voice ownership retains original releases.')
 cfg['code_bytes']+=sum(r['bytes'] for r in dual['regions'])
full['components']+=dual['regions']+[{'name':'USB_mirror_private_state_seed','base':dual['USB_state'],'bytes':160}]
Path('work/os144/E09-PC-layout-main.bin').write_bytes(main)
Path('work/os144/E09-PC-layout-payload.bin').write_bytes(payload)
Path('work/os144/E09-PC-install-layout.json').write_text(json.dumps(native,indent=2))
Path('outputs/Digitone-E09-PC-path-layout.json').write_text(json.dumps(full,indent=2))
source=Path('work/package-E08C-controls-PC.py').read_text().replace('E08C','E09')
exec(compile(source,'E09-internal-PC-package','exec'))
assert sha(Path('outputs/Digitone_OS1.44E08F_M1_ARP_MENU_FIX_PC_ONLY.syx').read_bytes())=='085ef1cae6d22878da74acf4a756dd9a22389971f211208e9bd67ff349e146f8'
print('E09 PC routing candidate packaged. M2–M4 and step editor not added.')
