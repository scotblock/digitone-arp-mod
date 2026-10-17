from pathlib import Path
import json
joined_UI_original_reader=Path.read_text
joined_UI_cfg=json.loads(joined_UI_original_reader(Path('work/os144/PC_ONLY-persistent-admission.json')))
def joined_UI_read(path,*args,**kwargs):
 text=joined_UI_original_reader(path,*args,**kwargs)
 if path.name=='test-PC-release-reset-startup.py':
  anchor="   m.uc.mem_write(release_hook['site'],bytes.fromhex(release_hook['replacement']))"
  addition="""
  for ui_hook in joined_UI_cfg['hooks']:
   assert bytes(m.uc.mem_read(ui_hook['site'],ui_hook['length'])).hex()==ui_hook['stock']
   m.uc.mem_write(ui_hook['site'],bytes.fromhex(ui_hook['replacement']))
"""
  assert anchor in text;text=text.replace(anchor,anchor+addition).replace('release-reset-startup-','joined-UI-startup-')
 return text
Path.read_text=joined_UI_read
try:exec(compile(joined_UI_read(Path('work/test-PC-release-reset-startup.py')),'joined-UI-startup','exec'))
finally:Path.read_text=joined_UI_original_reader
