import json
from pathlib import Path
r=json.loads(Path('outputs/Digitone-E04-PC-parent-destruction-retained-callback.json').read_text())
for c in r['cases']:print({k:v for k,v in c.items() if k not in ['native_frees','failure']});print('free_count',len(c['native_frees']))
