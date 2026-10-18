"""Startup-copied E11 UI: native new controls and keyboard/sequence output."""
from pathlib import Path
s=Path('work/test-PC-E10-package-playback.py').read_text(encoding='utf-8')
s=s.replace('PC_ONLY-E10-package','PC_ONLY-E11-package').replace('Digitone-E10-PC-package-startup.json','Digitone-E11-PC-package-startup.json').replace('Digitone-E10-PC-package-playback.json','Digitone-E11-PC-packaged-playback.json')
anchor="exec(compile(source,'E10-packaged-native-editor-playback','exec'))"
extra='''
inner="exec(compile(source,'E10-copied-native-editor-and-playback','exec'))"
inject="""
source=source.replace('for _ in range(12):s.turn(3,-16,after_ms=100)','for _ in range(12):s.turn(6,-16,after_ms=100)')
source=source.replace('s.turn(5,16,after_ms=100)',"s.tap(s.code('RIGHT'),hold_ms=80,after_ms=100)")
source=source.replace('for _ in range(step):s.turn(6,16,after_ms=100)','for _ in range(step):s.turn(5,16,after_ms=100)')
source=source.replace('if step==2:s.turn(7,16,after_ms=100)',"if step==2:s.tap(s.code('DOWN'),hold_ms=80,after_ms=100)")
source=source.replace('for _ in range(3):s.turn(5,-16,after_ms=100)',"for _ in range(3):s.tap(s.code('LEFT'),hold_ms=80,after_ms=100)")
source=source.replace('outputs/Digitone-E10-PC-package-playback.json','outputs/Digitone-E11-PC-packaged-playback.json')
"""
assert inner in source;source=source.replace(inner,inject+'\\n'+inner)
'''
assert anchor in s;s=s.replace(anchor,extra+'\n'+anchor)
exec(compile(s,'E11-copied-UI-playback','exec'))
import json
p=Path('outputs/Digitone-E11-PC-packaged-playback.json');r=json.loads(p.read_text());assert r['passed']
r.update(E11_UI_startup_copied=True,helpers_host_loaded=False,hooks_host_patched=False,hardware_ready=False)
r['limits']=['E11 internal package, actual stock loader handoff, native cold copier/init/logo/UI, then separate native playback session. Serialized seams and peripheral models remain.','Arrow/E/F programming uses copied E11 code; no executable helper/hook/settings host overlay. MIDI gate/routing/USB endpoint fixtures remain.','E10 storage format and existing main arp controls retained. No physical timing/cache or device update guarantee.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
