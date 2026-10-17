"""Separate E08F PC candidate; require native panel comparison before packaging."""
from pathlib import Path
import json,hashlib
panel=json.loads(Path('outputs/Digitone-E08E-PC-menu-panel.json').read_text())
assert panel['passed']
assert json.loads(Path('outputs/Digitone-E08E-PC-menu-fix-contracts.json').read_text())['passed']
fix=json.loads(Path('work/os144/PC_ONLY-E08E-menu-fix-layout.json').read_text())
payload=Path('work/os144/PC_ONLY-E08E-menu-fix-payload.bin').read_bytes()
old=Path('work/os144/E08E-PC-layout-payload.bin').read_bytes()
main=bytearray(Path('work/os144/E08E-PC-layout-main.bin').read_bytes())
native=json.loads(Path('work/os144/E08E-PC-install-layout.json').read_text())
full=json.loads(Path('outputs/Digitone-E08E-PC-path-layout.json').read_text())
off=native['copy_source']-0x40000400
assert bytes(main[off:off+len(old)])==old
assert len(old)==len(payload)
main[off:off+len(old)]=payload
sha=lambda x:hashlib.sha256(x).hexdigest()
for cfg in [native,full]:
    for field in ['regions','components']:
        for r in cfg.get(field,[]):
            f=next((f for f in fix['regions'] if f['base']==r['base']),None)
            if f:r['bytes']=f['bytes']
    cfg.update(main_sha256=sha(main),payload_sha256=sha(payload),menu_routing_corrected=True,
      parent_build='E08E',PC_only=True,hardware_ready=False,
      menu_changes=fix['changes'],menu_helper_delta_bytes=sum(r['bytes']-r['old_bytes'] for r in fix['regions']))
    cfg['code_bytes']+=cfg['menu_helper_delta_bytes']
Path('work/os144/E08F-PC-layout-main.bin').write_bytes(main)
Path('work/os144/E08F-PC-layout-payload.bin').write_bytes(payload)
Path('work/os144/E08F-PC-install-layout.json').write_text(json.dumps(native,indent=2))
Path('outputs/Digitone-E08F-PC-path-layout.json').write_text(json.dumps(full,indent=2))
source=Path('work/package-E08C-controls-PC.py').read_text().replace('E08C','E08F')
exec(compile(source,'E08F-PC-menu-package','exec'))
assert sha(Path('outputs/Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx').read_bytes())=='74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3'
print('E08F internal PC package created; E08E unchanged. Not a hardware release.')
