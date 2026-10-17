from pathlib import Path
import json
input_startup_original_read=Path.read_text
startup_input_cfg=json.loads(Path('work/os144/PC_ONLY-input-live-overlay.json').read_text())
def input_startup_source_read(path,*args,**kwargs):
 s=input_startup_original_read(path,*args,**kwargs)
 if path.name=='test-PC-startup-queued-DIN.py':
  s=s.replace('startup-queued-DIN-','input-live-startup-')
 if path.name=='test-PC-cold-permit-boundary.py':
  anchor="  row['admission_boundary_events']=[];"
  installation=r'''
  input_code=Path('work/os144/PC_ONLY-input-live-overlay.bin').read_bytes()
  m.load(input_code,startup_input_cfg['base']);m.install_isa_patches_scoped(input_code,startup_input_cfg['base'])
  for hook in startup_input_cfg['hooks']:
   assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']
   m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))
'''
  assert anchor in s;s=s.replace(anchor,installation+'\n'+anchor)
 if path.name=='test-PC-native-cold-admission-startup.py':
  s=s.replace('[0,0x434f4c44,0x494e4954]','[0,0x434f4c44,0x494e4954,0x4c495645]')
 if path.name=='test-PC-ISA-corrected-startup.py':
  old="('E04_restored','work/os144/PC_ONLY-saved-mirror-valid_first.img')"
  assert old in s;s=s.replace(old,old+",('E04_disabled','work/os144/PC_ONLY-saved-mirror-valid_first.img')")
  s=s.replace("name=='E04_bad_pointer'","name in ['E04_bad_pointer','E04_disabled']")
  s=s.replace("disabled=name in ['E04_bad_pointer','E04_post_stock_bad_magic']","disabled=name in ['E04_bad_pointer','E04_post_stock_bad_magic','E04_disabled']")
 if path.name=='test-PC-atomic-storage-startup.py':s=s.replace("len(out['cases'])==2","len(out['cases'])==3")
 return s
Path.read_text=input_startup_source_read
try:exec(compile(input_startup_source_read(Path('work/test-PC-startup-queued-DIN.py')),'input-guards-LIVE-startup','exec'))
finally:Path.read_text=input_startup_original_read
