from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E04-PC-queued-pattern-retirement-controls.json').read_text())
for c in r['cases']:
 print(c['mode'],c['passed']);print([(x['kind'],x.get('descriptor'),x.get('owner_field'),x.get('replacement')) for x in c['events']])
