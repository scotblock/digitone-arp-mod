"""Integrate only the tested owner correction; preserve all E09 artifacts."""
from pathlib import Path
import json,struct,hashlib,shutil
sha=lambda b:hashlib.sha256(b).hexdigest()
proof=json.loads(Path('outputs/Digitone-E09-native-sequence-owner-fixed.json').read_text())
assert proof['passed'] and proof['sequenced_pulse_count']>=3
assert json.loads(Path('outputs/Digitone-E09-PC-sequence-owner-contracts.json').read_text())['passed']
full=json.loads(Path('outputs/Digitone-E09-PC-path-layout.json').read_text())
native=json.loads(Path('work/os144/E09-PC-install-layout.json').read_text())
fix=json.loads(Path('work/os144/PC_ONLY-E09-sequence-owner-helper.json').read_text())
code=Path('work/os144/PC_ONLY-E09-sequence-owner-helper.bin').read_bytes()
payload=bytearray(Path('work/os144/E09-PC-layout-payload.bin').read_bytes())
offset=fix['region']['base']-native['base']
assert sha(payload[offset:offset+len(code)])==fix['before_sha256']
payload[offset:offset+len(code)]=code
main=bytearray(Path('work/os144/E09-PC-layout-main.bin').read_bytes())
source=full['copy_source']-0x40000400
assert main[source:source+len(payload)]==Path('work/os144/E09-PC-layout-payload.bin').read_bytes()
main[source:source+len(payload)]=payload
for cfg in [full,native]:
    cfg.update(parent_build='E09',PC_only=True,hardware_ready=False,main_sha256=sha(main),payload_sha256=sha(payload),
               M1_sequence_owner_fix=True,patch_only_existing_region=fix['region'],additional_copy_bytes_over_E09=0,
               limitations=['M1 only; M2–M4 and step editor remain unimplemented.','Physical validation, saved-project persistence and queued-note ownership across every transition remain unverified.'])
Path('work/os144/E09A-PC-layout-main.bin').write_bytes(main)
Path('work/os144/E09A-PC-layout-payload.bin').write_bytes(payload)
Path('work/os144/E09A-PC-install-layout.json').write_text(json.dumps(native,indent=2))
Path('outputs/Digitone-E09A-PC-path-layout.json').write_text(json.dumps(full,indent=2))
source=Path('work/package-E08C-controls-PC.py').read_text().replace('E08C','E09A')
exec(compile(source,'E09A-internal-PC-package','exec'))
candidate=Path('work/os144/E09A-PC-path-candidate.syx')
full=json.loads(Path('outputs/Digitone-E09A-PC-path-layout.json').read_text())
full.update(candidate_sha256=sha(candidate.read_bytes()),syx_bytes=candidate.stat().st_size)
Path('outputs/Digitone-E09A-PC-path-layout.json').write_text(json.dumps(full,indent=2))
assert sha(Path('outputs/Digitone_OS1.44E09_DUAL_PORT_ARP_PC_ONLY.syx').read_bytes())=='2d7446c086699918ed882a7f9e52ac6e29657d09557a4be519b1500bfcd710f0'
Path('work/test-E09A-packaged-panel-playback.py').write_text(Path('work/test-E09-packaged-panel-playback.py').read_text().replace('E09','E09A'))
print('Created separate E09A PC candidate',sha(candidate.read_bytes()),'no device contacted')
