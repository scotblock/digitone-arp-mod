import json,pathlib
r=json.loads(pathlib.Path('outputs/Digitone-actual-capture-and-pitch-instruction-results.json').read_text())
print([(n,v['size']) for n,v in r['new_fixture_disassembly'].items()]);print(r['pipeline_cases'])
