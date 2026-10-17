from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E08-tempo-clock-discovery.json').read_text());print(r['tempo_samples'],r['failure'])
p=Path('work/test-E08-M1-native-contracts.py').read_text().replace('E08-PC-native-M1','E08-PC-tempo-M1').replace('Digitone-E08-M1-native-contracts','Digitone-E08-M1-tempo-contracts')
p=p.replace('0x400f4000]','0x400f4000,0x47be2840]')
p=p.replace("put(S+4,1);put(TP,1);", "put(S+4,1);put(TP,1);put(0x47be2840,0x4c495645);")
a=p.index("assert bytes(u.mem_read(S-8,8))")
p=p[:a]+'''for index,units in enumerate(c['rate_units']):
 for pct in [1,25,50,75,99]:
  init();assert invoke(c['entries']['configure'],[index,pct])==1;assert get(S+32)==units and get(S+36)==units*pct//200 and get(S+304)==index and get(S+308)==pct
checks.append('all native rate/gate choices in musical clock units')
for index,pct in [(8,50),(0xffffffff,50),(2,0),(2,100)]:
 init();before=bytes(u.mem_read(S+32,8));assert invoke(c['entries']['configure'],[index,pct])==0 and bytes(u.mem_read(S+32,8))==before
checks.append('invalid musical settings preserve prior configuration')
init();raw=src();put(0x47be2840,0x434f4c44);assert dispatch()==SRC and bytes(u.mem_read(SRC,52))==raw and get(S+8)==0
checks.append('COLD admission bypasses capture and generation')
''' +p[a:]
Path('work/test-E08-M1-tempo-contracts.py').write_text(p)
