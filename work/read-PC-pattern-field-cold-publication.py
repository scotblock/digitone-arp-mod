import json
from pathlib import Path
r=json.loads(Path('outputs/Digitone-E04-PC-pattern-field-cold-publication.json').read_text())['cases'][0]
for k in ['owner_field_writes','owner_setter_entries','large_allocation_requests']:print(k,r[k])
