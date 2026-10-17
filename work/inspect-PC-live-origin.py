from pathlib import Path
import json,collections
r=json.loads(Path('outputs/Digitone-E04-PC-live-context-trace.json').read_text())['cases'][0]
t=r['trace'];first=next(x for x in t if x['label']=='commit' and x['stack'][3]==0);e=hex(first['regs']['A3'])
print('target',e,'at',first['ms'])
for x in r['allocations']:
 if x['event']==e and x['ms']<=first['ms']:print('ALLOC',x['ms'],x['stage'],[hex(a) for a in x['stack']])
for x in t:
 if x['label'] in ['stock queue_publish','producer_capture','stock acceptance']:
  print(x['label'],round(x['ms'],4),x['stage'],hex(x['regs']['A3']),[hex(a) for a in x['stack'][:4]],[(v['address'],v['fields'][0],v['fields'][6]>>24,v['context']) for v in x['events'] if v['slot']])
slot=next(v['slot'] for v in first['events'] if v['address']==e)
print('SLOT writes',slot)
for x in r['metadata_writes']:
 if x['address']==slot and x['ms']<=first['ms']:print(x)
print('read branches')
for x in r['helper_paths']:
 if x['name']=='read' and abs(x['ms']-9027.333)<.02:print(x)
