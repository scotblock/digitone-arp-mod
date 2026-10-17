import json,pathlib
j=json.loads(pathlib.Path('outputs/Digitone-shared-memory-pilot.json').read_text());r=j['runs'][0]
print(json.dumps(r['memory_model'],indent=2));print('pilot elapsed',j['elapsed_seconds'])
