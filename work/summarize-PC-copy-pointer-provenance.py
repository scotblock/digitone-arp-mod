import json,collections
from pathlib import Path
r=json.loads(Path('outputs/Digitone-E04-PC-copy-pointer-provenance-runtime.json').read_text())
print('passed',r['passed'],'model_ms',r['elapsed_model_ms'],'pattern',r['pattern_replacement_confirmed'])
for name in ['pattern_entries','buffer_entries','buffer_allocations','target_copies']:
 rows=r[name];print(name,len(rows));print(rows[:5]);print('callers',collections.Counter(x['caller'] for x in rows))
