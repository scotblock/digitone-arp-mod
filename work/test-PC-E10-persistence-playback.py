"""Regression: copied persistence image still supports panel-created arp playback."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-integrated-playback.py').read_text(encoding='utf-8')
for old,new in [
 ('PC_ONLY-E10-startup','PC_ONLY-E10-persistence'),
 ('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-persistence-startup.json'),
 ('Digitone-E10-PC-integrated-playback.json','Digitone-E10-PC-persistence-playback.json'),
 ('native_project_persistence=False','native_project_persistence=True'),
]:source=source.replace(old,new)
exec(compile(source,'E10-native-persistence-playback','exec'))
p=Path('outputs/Digitone-E10-PC-persistence-playback.json')
r=json.loads(p.read_text());r['editor_to_pattern_bank_connected']=False
r.setdefault('limits',[]).append('Persistence hooks are installed, but this playback regression programs active state through the panel; saved-bank recall is not connected.')
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
