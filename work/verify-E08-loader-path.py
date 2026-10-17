from pathlib import Path
# Retain the matching tempo/playback verifier; remove obsolete overlay claims.
s=Path('work/verify-E08-tempo-and-loading.py').read_text().split("layout=json.loads")[0]
s=s.replace('Digitone-E08-M1-tempo-playback.json','Digitone-E08-loader-playback.json')
s=s.replace("r['limits']=[", "r['overlay_verifier_limits_superseded']=[")
exec(compile(s,'E08-native-path-verifier','exec'))
import json,hashlib
r=json.loads(Path('outputs/Digitone-E08-loader-playback.json').read_text())
loader=json.loads(Path('outputs/Digitone-E08-packed-loader.json').read_text());startup=json.loads(Path('outputs/Digitone-E08-PC-startup-comparison.json').read_text());layout=json.loads(Path('outputs/Digitone-E08-PC-path-layout.json').read_text())
assert loader['passed'] and startup['passed'] and r['passed'] and r['loader_startup_state_verified'] and not r['helpers_host_loaded']
r['limits']=['The stock loader, native copier, initializer and playback execute across serialized modeled-state handoffs. Hardware peripherals and ISA compatibility are modeled; physical cache coherence and timing remain unverified.','Mode enable and rate/gate requests are test fixtures; no native settings page or project persistence yet.','M1 only; no proof of every reset, sustain, mute, pattern or track route.']
r.pop('overlay_verifier_limits_superseded',None)
Path('outputs/Digitone-E08-loader-playback.json').write_text(json.dumps(r,indent=2))
summary={'PC_only':True,'passed':True,'candidate_sha256':layout['candidate_sha256'],'loader_instructions':loader['instructions'],'startup_cases':len(startup['cases']),'note_on_count':r['note_on_count'],'matching_note_off_count':r['matching_note_off_count'],'helpers_host_loaded':False,'hardware_ready':False,'limits':r['limits']}
Path('outputs/Digitone-E08-loader-startup-playback-results.json').write_text(json.dumps(summary,indent=2));print(summary)
