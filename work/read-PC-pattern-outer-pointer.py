import json
from pathlib import Path
r=json.loads(Path('outputs/Digitone-E04-PC-pattern-outer-pointer-runtime.json').read_text());print(r['outer_dispatch'])
