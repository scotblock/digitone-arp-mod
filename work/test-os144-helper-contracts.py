from pathlib import Path
import json
port=json.loads(Path('work/os144/helper-port.json').read_text());info=json.loads(Path('work/packed-context-build.json').read_text())
mapping=port['mapping']
def addresses(source):
 for old,new in mapping.items():source=source.replace(old,new)
 # Hook entry addresses do not occur as helper operands.
 for h in port['hooks']:source=source.replace(h['old_site'],h['site'])
 return source
s=Path('work/test-packed-context-overlay.py').read_text()
s=addresses(s)
s=s.replace("pathlib.Path('work/'+name+'.bin')","pathlib.Path('work/os144/'+name+'.bin')")
s=s.replace('Digitone-packed-context-differential-checks.json','Digitone-OS1.44-helper-differential.json')
s=s.replace("'build_sha256':info['sha256']", "'build_sha256':port['PC_only_helper_images'][0]['sha256'],'reference_142_packed_sha256':info['sha256']")
# The existing copy test is rendered separately so every operand is ported.
s=s.split('# Reuse the existing stock memcpy')[0]
exec(compile(s,'OS1.44-differential-contracts','exec'))
s=Path('work/test-cache-context-helpers.py').read_text()
s=addresses(s).replace('work/cache-context-overlay.bin','work/os144/packed-context-overlay.bin').replace('work/section-3.bin','work/os144/section-3.bin')
s=s.replace("json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())","info['layout']")
s=s.replace("json.loads(pathlib.Path('work/cache-context-build.json').read_text())","dict(slot_address=info['layout']['slot']['address'],copy_address=info['layout']['copy']['address'],first_copy_address=info['layout']['first_copy']['address'],hooks=[0x40093d46,0x4009418a])")
s=s.replace('m.install_isa_patches_scoped(blob,RAM)',"m.install_isa_patches_scoped(blob[:info['code_bytes']],RAM)")
s=s.replace('Digitone-cache-context-helper-checks.json','Digitone-OS1.44-helper-copy.json')
exec(compile(s,'OS1.44-copy-contracts','exec'))
