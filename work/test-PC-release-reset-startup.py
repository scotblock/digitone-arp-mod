from pathlib import Path
import json
release_startup_reader=Path.read_text
release_startup_cfg=json.loads(release_startup_reader(Path('work/os144/PC_ONLY-release-reset-overlay.json')))
def release_startup_read(path,*args,**kwargs):
 text=release_startup_reader(path,*args,**kwargs)
 if path.name=='test-PC-input-live-startup.py':
  anchor="   assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']\n   m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))"
  addition="""
  release_code=Path('work/os144/PC_ONLY-release-reset-overlay.bin').read_bytes()
  m.load(release_code,release_startup_cfg['base']);m.install_isa_patches_scoped(release_code,release_startup_cfg['base'])
  for release_hook in release_startup_cfg['hooks']:
   assert bytes(m.uc.mem_read(release_hook['site'],release_hook['length'])).hex()==release_hook['stock']
   m.uc.mem_write(release_hook['site'],bytes.fromhex(release_hook['replacement']))
"""
  assert anchor in text;text=text.replace(anchor,anchor+addition)
  text=text.replace('input-live-startup-','release-reset-startup-')
 return text
Path.read_text=release_startup_read
try:exec(compile(release_startup_read(Path('work/test-PC-input-live-startup.py')),'release-reset-startup','exec'))
finally:Path.read_text=release_startup_reader
