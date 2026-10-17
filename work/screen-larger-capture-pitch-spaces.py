exec(open('work/disassemble.py').read().split('out=[]')[0])
import json
r=json.loads(pathlib.Path('outputs/Digitone-executable-space-screening.json').read_text());runs=r['padding_runs'][:7]
for run in runs:
 lo=int(run['start'],16);hi=int(run['end_exclusive'],16);hits=[]
 for p in range(0,len(b)-3,2):
  v=int.from_bytes(b[p:p+4],'big')
  if lo<=v<hi:hits.append((hex(base+p),hex(v)))
 print(run['start'],run['length'],'hits',len(hits),hits[:10],'preceding',b[lo-base-12:lo-base].hex())
