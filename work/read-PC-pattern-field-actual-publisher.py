from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E04-PC-pattern-field-actual-publisher.json').read_text())['cases'][0]
print('SETTERS',r['owner_setter_entries']);print('WRITES',r['owner_field_writes'])
