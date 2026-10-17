"""Native editor/sequence playback from E10's copied cold-start state.

No E10 helper, hook, sequence settings or initialization is host-written here.
Inherited input/routing/USB endpoint fixtures remain disclosed by the scenario.
"""
from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E10-PC-integrated-startup.json').read_text());assert r['passed']
generator=Path('work/test-PC-E10-step-panel-playback.py').read_text().split("exec(compile(source,'E10-native-step-panel-playback'")[0]
ns={};exec(compile(generator,'E10-integrated-playback-generator','exec'),ns);source=ns['source']
anchor="exec(compile(prefix,'M1-both-port-definitions','exec'))"
replacements=[('outputs/Digitone-E09A-PC-path-layout.json','work/os144/PC_ONLY-E10-startup-full-layout.json'),('work/os144/E09A-PC-install-layout.json','work/os144/PC_ONLY-E10-startup-layout.json'),("folder/'E09A-PC-install-layout.json'","folder/'PC_ONLY-E10-startup-layout.json'"),('outputs/Digitone-E09A-PC-startup-comparison.json','outputs/Digitone-E10-PC-integrated-startup.json'),("folder/'E09A-PC-layout-payload.bin'","folder/'PC_ONLY-E10-startup-payload.bin'"),("folder/'E09A-PC-layout-main.bin'","folder/'PC_ONLY-E10-startup-main.bin'")]
injection=''
for old,new in replacements:injection+='prefix=prefix.replace('+repr(old)+','+repr(new)+')\n'
assert anchor in source;source=source.replace(anchor,injection+anchor)
start=source.index('before_step_install=install');end=source.index("s=Session(case['ui_snapshot']",start)
source=source[:start]+source[end:]
source=source.replace('state_initialization_is_fixture=True','state_initialization_is_fixture=False')
source=source.replace('outputs/Digitone-E10-PC-step-panel-playback.json','outputs/Digitone-E10-PC-integrated-playback.json')
source=source.replace("s=Session(case['ui_snapshot']", "out.update(firmware_container_created=False,loader_derived_E10_state=False,native_project_persistence=False,automatic_pattern_binding=False)\ns=Session(case['ui_snapshot']")
exec(compile(source,'E10-copied-native-editor-and-playback','exec'))
