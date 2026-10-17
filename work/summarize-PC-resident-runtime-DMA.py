from pathlib import Path
import json,collections
p=Path('outputs/Digitone-E04-PC-resident-storage-extended-runtime.json');r=json.loads(p.read_text());channels={};links=collections.Counter();unknown=collections.Counter()
for v in r['DMA'].values():
 c=channels.setdefault(v['channel'],{'observations':0,'lowest':v['low'],'highest':v['high'],'overlap_count':0,'unknown_count':0,'scatter_count':0})
 c['observations']+=1;c['lowest']=hex(min(int(c['lowest'],16),int(v['low'],16)));c['highest']=hex(max(int(c['highest'],16),int(v['high'],16)));c['overlap_count']+=v['overlaps_queue'];c['unknown_count']+=bool(v['unknown']);c['scatter_count']+=v['scatter_gather']
 if v['scatter_gather']:links[(v['channel'],v['next_descriptor'])]+=1
 for label in v['unknown']:unknown[label]+=1
r['DMA_observation_count']=len(r['DMA']);r['DMA_channels']=channels;r['DMA_scatter_links']=[{'channel':ch,'descriptor':ptr,'observations':n} for (ch,ptr),n in links.items()];r['DMA_unknown_encodings']=dict(unknown);r['DMA_example_descriptors']=list(r['DMA'].values())[:12];del r['DMA'];p.write_text(json.dumps(r,indent=2));print('duration',r['elapsed_model_ms'],'bulk',r['bulk_calls'],'DMA',channels,'links',r['DMA_scatter_links'],'unknown',unknown,'replacement',r['pattern_replacement_confirmed'])
