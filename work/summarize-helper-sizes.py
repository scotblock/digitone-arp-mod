import json,pathlib
r=json.loads(pathlib.Path('outputs/Digitone-metadata-helper-instruction-tests.json').read_text())
print({k:v['bytes'] for k,v in r['helpers'].items()})
