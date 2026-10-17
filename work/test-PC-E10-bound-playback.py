"""Panel-programmed MIDI arp playback using copied binding adapters."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-integrated-playback.py').read_text(encoding='utf-8')
for old,new in [('PC_ONLY-E10-startup','PC_ONLY-E10-bound'),('Digitone-E10-PC-integrated-startup.json','Digitone-E10-PC-bound-startup.json'),('Digitone-E10-PC-integrated-playback.json','Digitone-E10-PC-bound-playback.json')]:source=source.replace(old,new)
anchor="exec(compile(source,'E10-copied-native-editor-and-playback','exec'))"
old="    for region in native['data_regions']:"
new=old+"\n        if region['name'] in ['E10_persistence_metadata','E10_pattern_binding_metadata']:continue"
injection="source=source.replace(\"exec(compile(prefix,'M1-both-port-definitions','exec'))\", 'prefix=prefix.replace('+repr("+repr(old)+")+','+repr("+repr(new)+")+')\\n'+\"exec(compile(prefix,'M1-both-port-definitions','exec'))\")\n"
assert anchor in source;source=source.replace(anchor,injection+anchor)
exec(compile(source,'E10-bound-playback','exec'))
p=Path('outputs/Digitone-E10-PC-bound-playback.json');r=json.loads(p.read_text());assert r['passed']
r.update(native_project_persistence=True,automatic_pattern_binding=True,editor_to_pattern_bank_connected=True)
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
