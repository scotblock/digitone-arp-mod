"""Native copied lifecycle-image keyboard/sequencer regression."""
from pathlib import Path
import json
source=Path('work/test-PC-E10-bound-playback.py').read_text(encoding='utf-8')
source=source.replace('PC_ONLY-E10-bound','PC_ONLY-E10-life').replace('Digitone-E10-PC-bound-startup.json','Digitone-E10-PC-life-startup.json').replace('Digitone-E10-PC-bound-playback.json','Digitone-E10-PC-life-playback.json')
source=source.replace("['E10_persistence_metadata','E10_pattern_binding_metadata']","['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']")
exec(compile(source,'E10-life-native-playback','exec'))
p=Path('outputs/Digitone-E10-PC-life-playback.json');r=json.loads(p.read_text());assert r['passed']
r['limits']=['Copied lifecycle code, native panel programming and keyboard/sequencer playback; inherited MIDI input/routing/USB endpoint fixtures remain.','Physical timing, power loss, cache behavior and other reset/copy paths remain uncertified.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
