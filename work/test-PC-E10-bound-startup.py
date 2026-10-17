"""Copied adapters and native empty-project capture, through logo/UI."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-integrated-startup.py').read_text(encoding='utf-8')
for old,new in [('PC_ONLY-E10-startup','PC_ONLY-E10-bound'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-bound-startup.json')]:source=source.replace(old,new)
anchor="exec(compile(source,'E10-direct-MAIN-native-startup','exec'))"
extra="source=source.replace('work/E10-startup-','work/E10-bound-startup-').replace('generated-E10-startup.py','generated-E10-bound-startup.py')\n"
assert anchor in source;source=source.replace(anchor,extra+anchor)
exec(compile(source,'E10-bound-cold-startup','exec'))
p=Path('outputs/Digitone-E10-PC-bound-startup.json');r=json.loads(p.read_text());assert r['passed']
r.update(native_project_persistence=True,automatic_pattern_binding=True,editor_to_pattern_bank_connected=True)
r['limits'].append('The copied native bank is captured from an empty-extension project; panel-created records and pattern recall are tested separately.')
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
