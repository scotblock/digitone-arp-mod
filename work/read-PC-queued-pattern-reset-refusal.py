from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E04-PC-queued-pattern-reset-refusal-controls.json').read_text())
for c in r['cases']:
 print(c['mode'],c['passed'],[(e['kind'],e.get('phase'),e.get('field')) for e in c['events'] if e['kind'].startswith('guard') or e['kind']=='native_conversion'])
