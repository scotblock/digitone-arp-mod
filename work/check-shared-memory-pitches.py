import pathlib,json
j=json.loads(pathlib.Path('outputs/Digitone-shared-memory-long-comparison.json').read_text())
for r in j['runs']:
 print(r['mode'],'pitches',[(round(x['ms'],3),x['track'],x['fixed_note']/65536) for x in r['pitch']])
 if r['quantizer_calls']:print('quantizer',[(x['note'],x['expected'],x['word']) for x in r['quantizer_calls']])
