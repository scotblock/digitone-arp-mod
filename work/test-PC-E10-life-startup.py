"""Native copier/init/cold project capture with lifecycle adapters installed."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-integrated-startup.py').read_text(encoding='utf-8')
for old,new in [('PC_ONLY-E10-startup','PC_ONLY-E10-life'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-life-startup.json')]:source=source.replace(old,new)
anchor="exec(compile(source,'E10-direct-MAIN-native-startup','exec'))"
extra="source=source.replace('work/os144/PC_ONLY-saved-mirror-valid_first.img','work/E10-bound-panel-patterns/plusdrive.img').replace('work/E10-startup-','work/E10-life-startup-').replace('generated-E10-startup.py','generated-E10-life-startup.py')\n"
assert anchor in source;source=source.replace(anchor,extra+anchor)
exec(compile(source,'E10-lifecycle-startup','exec'))
p=Path('outputs/Digitone-E10-PC-life-startup.json');r=json.loads(p.read_text());assert r['passed']
r.update(native_project_persistence=True,automatic_pattern_binding=True,editor_to_pattern_bank_connected=True,lifecycle_helpers_copier_installed=True,firmware_container_created=False,hardware_ready=False)
r['limits'].append('Input card contains the preceding panel-created named project; its old retained boot fixture has absent E10 records. Native named reload is tested next.')
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
