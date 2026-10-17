import json,pathlib
j=json.loads(pathlib.Path('outputs/Digitone-memory-sensitivity-40.json').read_text());r=j['runs'][0]
print('failure',j['failure'],'control',r['initial_control_registers'],'data',r['data_access_totals'])
w=r['data_cache_windows'];print('windows',len(w));print('worst',max(w,key=lambda x:x['wall_cycles']))
for p in [0,4,8,16,20]:
 cost=[x['wall_cycles']+p*(x.get('fills',0)+x.get('dirty_evictions',0)) for x in w]
 print(p,'max',max(cost),'late250',sum(v>166667 for v in cost),'late264',sum(v>176000 for v in cost))
