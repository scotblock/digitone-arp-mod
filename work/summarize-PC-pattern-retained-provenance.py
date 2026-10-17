import json
from pathlib import Path
r=json.loads(Path('outputs/Digitone-E04-PC-pattern-retained-provenance-runtime.json').read_text())
for k in ['retained_construction','retained_callbacks','pattern_entries']:print(k,r[k])
