from pathlib import Path
p=Path('work/test-PC-deferred-release-startup.py');s=p.read_text();s=s.replace("  for deferred_hook in native_defer_spec['hooks']:\n   assert", "  for deferred_hook in [h for h in native_defer_spec['hooks'] if h['name']!='completion_dispatch']:\n   assert")
anchor=" if path.name=='test-PC-ISA-corrected-startup.py':"
extra=""" if path.name=='test-PC-native-cold-admission-startup.py':
  anchor=\"  m.load(state_code,native_admission_cfg['base']);m.install_isa_patches_scoped(state_code,native_admission_cfg['base'])\"
  addition=\"\\n  completion_hook=next(h for h in native_defer_spec['hooks'] if h['name']=='completion_dispatch')\\n  assert bytes(m.uc.mem_read(completion_hook['site'],completion_hook['length'])).hex()==completion_hook['previous']\\n  m.uc.mem_write(completion_hook['site'],bytes.fromhex(completion_hook['replacement']))\"
  assert anchor in text;text=text.replace(anchor,anchor+addition)
"""
s=s.replace(anchor,extra+anchor);p.write_text(s)
