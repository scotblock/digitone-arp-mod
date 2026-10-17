"""Isolated no-memory-stall costs, distinct from playback timing sensitivity."""
import pathlib,json
exec(pathlib.Path('work/test-indexed-context-lookup.py').read_text().split('started=time.monotonic()')[0])
from emu.cftiming import CycleClock
clocks=[CycleClock(m,idle=set(),fsys=264000000,stalls=False,icache=False) for m in machines]
rows=[]
for index in [0,1,2,16,64,127,128]:
 for name in ['snapshot','candidate_store']:
  costs=[]
  for m,c in zip(machines,clocks):
   before=(c.cycles,c.instructions)
   invoke(m,layout[name]['address'],[POOL+index*72,0x800000bd] if name=='candidate_store' else [POOL+index*72])
   costs.append({'cycles':c.cycles-before[0],'instructions':c.instructions-before[1]})
  rows.append({'helper':name,'slot':index,'previous':costs[0],'indexed':costs[1]})
out={'firmware_modified':False,'model':'isolated cycle decoder, memory/cache stalls disabled; not hardware measurements','cases':rows}
pathlib.Path('outputs/Digitone-indexed-context-lookup-costs.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
