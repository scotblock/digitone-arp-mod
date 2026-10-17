"""Retest actual arp capture/acceptance/pitch fixtures at reserved addresses."""
import pathlib,json
p=pathlib.Path('work/test-reserved-RAM-route.py').read_text();exec(p[:p.index('m=fresh();')])
# Reuse the original integration cases with the tested relocated helper bodies.
h['names']={name:item['address'] for name,item in layout.items()}
h['fixtures']={item['address']:runblob[item['address']-RAM:item['address']-RAM+item['size']] for item in layout.values()}
h['RANGES'].extend((addr,addr+len(code)) for addr,code in h['fixtures'].items())
body=pathlib.Path('work/test-actual-capture-and-pitch.py').read_text().split('\nchecks=[];cases=[];OWNER=')[1].split('\nnew_bodies=')[0]
body='checks=[];cases=[];OWNER='+body
body=body.replace('OWNER=0x28000000',f'OWNER={BSS-0x14100}')
body=body.replace('m.write(0x4199d590,4,OWNER)',f'm.map({PTR},4);m.map(0x28000000,0x14100);m.write(0x4199d590,4,0x28000000);m.write({PTR},4,OWNER)')
body=body.replace("'null_owner':(0x4199d590,0)",f"'null_owner':({PTR},0)")
exec(compile(body,'reserved-arp-integration','exec'),h)
assert all(machine.read(0x4199d590,4)==0x28000000 for machine,event,track in h['pipelines'])
r={'checks':h['checks'],'check_count':len(h['checks']),'quantizer_comparisons':h['quant_cases'],'pipeline_cases':h['cases'],'stock_owner_preserved':True,'metadata':hex(BSS),'firmware_modified':False,'limits':['Same supplied finalization/writer gates and input fields as prior instruction integration suite.','Full live/held/queued producer coverage and asynchronous scheduling unproven.','Initialized reserved header supplied; boot and initializer are tested separately.','RAM ownership for OS1.42 and hardware execution not certified.']}
pathlib.Path('outputs/Digitone-reserved-RAM-arp-integration-results.json').write_text(json.dumps(r,indent=2));print('PASS',len(h['checks']),'reserved-address integration assertions')
