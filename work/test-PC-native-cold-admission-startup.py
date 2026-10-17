"""Native host-loaded PC hooks; original firmware/raw files remain untouched."""
from pathlib import Path
import json
native_boot_original_read=Path.read_text
native_boot_cfg=json.loads(Path('work/os144/PC_ONLY-cold-admission-overlay.json').read_text())
native_admission_cfg=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text())
def native_boot_source_read(path,*args,**kwargs):
 s=native_boot_original_read(path,*args,**kwargs)
 if path.name=='test-PC-cold-permit-boundary.py':
  s=s.replace('cold-permit-boundary-','native-cold-admission-').replace('Digitone-E04-PC-cold-permit-boundary.json','Digitone-E04-PC-native-cold-admission-startup.json')
  anchor="  row['admission_boundary_events']=[];"
  installation=r'''
  native_code=Path('work/os144/PC_ONLY-cold-admission-overlay.bin').read_bytes()
  state_code=Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()
  m.load(native_code,native_boot_cfg['base']);m.install_isa_patches_scoped(native_code,native_boot_cfg['base'])
  m.load(state_code,native_admission_cfg['base']);m.install_isa_patches_scoped(state_code,native_admission_cfg['base'])
  for hook in native_boot_cfg['hooks']:
   assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']
   m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))
'''
  assert anchor in s;s=s.replace(anchor,installation+'\n'+anchor)
  old="uc.mem_write(0x47be2840,struct.pack('>I',0x434f4c44));event['fixture_marker_seeded']=True"
  assert old in s;s=s.replace(old,"event['native_seed_hook_follows']=True")
  s=s.replace("row['cold_marker_fixture_only']=True","row['cold_marker_fixture_only']=False;row['native_boot_helpers_host_loaded']=True")
  s=s.replace("assert value==0x434f4c44 and event['stack_return']","assert value==0x494e4954 and event['stack_return']")
  s=s.replace("assert row['admission_word_writes']==[{'pc':'0x4029c4c2','address':'0x47be2840','size':4,'value':0}]","assert [w['value'] for w in row['admission_word_writes']]==[0,0x434f4c44,0x494e4954]")
  s=s.replace("row['cold_marker_survives_to_initializer']=True","row['native_cold_seed_consumed_before_initializer']=True")
 return s
Path.read_text=native_boot_source_read
try:exec(compile(native_boot_source_read(Path('work/test-PC-cold-permit-boundary.py')),'native-cold-admission-startup','exec'))
finally:Path.read_text=native_boot_original_read
