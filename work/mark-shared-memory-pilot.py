import json,pathlib
p=pathlib.Path('outputs/Digitone-shared-memory-pilot.json');j=json.loads(p.read_text())
j['diagnostic_only']=True
j['superseded_reason']='Early pilot preceded previous-DONE masking and first-execution cache-hook corrections. Do not use as validated final timing evidence.'
p.write_text(json.dumps(j,indent=2))
print('Early pilot explicitly marked diagnostic only.')
