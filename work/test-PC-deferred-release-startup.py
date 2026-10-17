from pathlib import Path
import json
native_defer_original_read=Path.read_text
native_defer_spec=json.loads(native_defer_original_read(Path('work/os144/PC_ONLY-deferred-release-overlay.json')))
def native_defer_read(path,*args,**kwargs):
 text=native_defer_original_read(path,*args,**kwargs)
 if path.name=='test-PC-native-cold-admission-startup.py':
  anchor="  m.load(state_code,native_admission_cfg['base']);m.install_isa_patches_scoped(state_code,native_admission_cfg['base'])"
  addition="\n  completion_hook=next(h for h in native_defer_spec['hooks'] if h['name']=='completion_dispatch')\n  assert bytes(m.uc.mem_read(completion_hook['site'],completion_hook['length'])).hex()==completion_hook['previous']\n  m.uc.mem_write(completion_hook['site'],bytes.fromhex(completion_hook['replacement']))"
  assert anchor in text;text=text.replace(anchor,anchor+addition)
 if path.name=='test-PC-ISA-corrected-startup.py':
  text=text.replace("exec(compile(s,'PC-ISA-corrected-startup','exec'))","Path('work/generated-deferred-startup-debug.py').write_text(s);exec(compile(s,'PC-ISA-corrected-startup','exec'))")
 if path.name=='test-PC-joined-UI-startup.py':
  anchor="   m.uc.mem_write(ui_hook['site'],bytes.fromhex(ui_hook['replacement']))"
  addition="""
  native_defer_code=Path('work/os144/PC_ONLY-deferred-release-overlay.bin').read_bytes()
  m.load(native_defer_code,native_defer_spec['base']);m.install_isa_patches_scoped(native_defer_code,native_defer_spec['base'])
  m.ensure(native_defer_spec['count']);m.uc.mem_write(native_defer_spec['count'],bytes(native_defer_spec['storage_bytes']))
  for deferred_hook in [h for h in native_defer_spec['hooks'] if h['name']!='completion_dispatch']:
   assert bytes(m.uc.mem_read(deferred_hook['site'],deferred_hook['length'])).hex()==deferred_hook['previous']
   m.uc.mem_write(deferred_hook['site'],bytes.fromhex(deferred_hook['replacement']))
"""
  assert anchor in text;text=text.replace(anchor,anchor+addition).replace('joined-UI-startup-','deferred-release-startup-')
 return text
Path.read_text=native_defer_read
try:exec(compile(native_defer_read(Path('work/test-PC-joined-UI-startup.py')),'deferred-release-startup','exec'))
finally:Path.read_text=native_defer_original_read
result=Path('outputs/Digitone-E04-PC-deferred-release-startup-startup.json');r=json.loads(result.read_text());r['deferred_queue_zero_initialized_by_host_fixture']=True;r['additional_storage_host_cleared']=True;r['limits'].append('New deferred-release queue is host-zeroed at installation; no owned/packaged native cold initialization is established.');result.write_text(json.dumps(r,indent=2))
