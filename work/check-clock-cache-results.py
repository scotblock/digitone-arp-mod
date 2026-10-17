import pathlib,json,hashlib
r=json.loads(pathlib.Path('outputs/Digitone-memory-sensitivity-40.json').read_text())['runs'][0]
print('icache',r['clock']['icache'],'fixture',len(r['candidate_fixture']))
for f in ['Digitone-cache-sensitivity-20.json','Digitone-memory-sensitivity-40.json']:
 j=json.loads((pathlib.Path('outputs')/f).read_text())
 print(f,j['elapsed_seconds'],[(x['mode'],x['clock']['icache'],x['render_deadline']) for x in j['runs']])
print('bootctlregs',json.loads(pathlib.Path('outputs/Digitone-clock-bootstrap-trace.json').read_text())['control_registers'])
