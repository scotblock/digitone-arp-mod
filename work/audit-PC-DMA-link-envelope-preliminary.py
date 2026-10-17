from pathlib import Path
import json,sys,struct,collections
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import edma_sw
r=json.loads(Path('outputs/Digitone-E04-PC-resident-DMA-successor-writers.json').read_text());c=collections.Counter();examples=[]
for key in r['DMA']:
 ch,raw=key.split(':',1);td=struct.unpack(edma_sw.TCD_FMT,bytes.fromhex(raw));target=edma_sw.link_channel(td[6])
 if target is None:continue
 c['target '+ch+'->'+str(target)]+=1
 if td[10]&16:c['ESG']=c.get('ESG',0)+1;continue
 mod=(td[1]>>3)&31;width=1<<(td[1]&7);count=edma_sw.iteration_count(td[9]);delta=count*((td[3]+width-1)//width)*td[7]+int.from_bytes(td[8].to_bytes(4,'big'),'big',signed=True)
 category='modulo bounded' if mod else 'no destination drift' if delta==0 else 'drift needs reachability check';c[category]+=1
 if category=='drift needs reachability check' and len(examples)<8:examples.append({'channel':ch,'dst':hex(td[5]),'delta':delta,'CSR':hex(td[10]),'CITER':hex(td[6]),'BITER':hex(td[9])})
print(dict(c));print(examples)
Path('outputs/Digitone-E04-PC-resident-DMA-link-envelope-preliminary.json').write_text(json.dumps({'PC_only':True,'counts':dict(c),'drift_examples':examples,'limits':['Characterizes observed descriptors only; self-link request/major reload behavior and subsequent reprogramming are not physically verified.']},indent=2))
