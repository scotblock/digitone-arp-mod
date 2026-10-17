import pathlib,json,hashlib
r=json.loads(pathlib.Path('outputs/Digitone-resident-caller-helper-tests.json').read_text())
print('checks',r['passed'],'instructions',r['instructions'],'cases',len(r['cases']),'end',r['layout_end_exclusive'])
print([(k,v['size'],v['address']) for k,v in r['fixtures'].items()])
for p in [pathlib.Path('work/section-3.bin'),pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')]:print(p.name,hashlib.sha256(p.read_bytes()).hexdigest())
