from pathlib import Path
import json,collections,sys,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import edma_sw
p=Path('outputs/Digitone-E04-PC-resident-DMA-successor-writers.json');r=json.loads(p.read_text());groups={};links={};drift=[];classes=collections.Counter()
for v in r['DMA'].values():
 c=groups.setdefault(v['channel'],{'descriptor_states':0,'min':v['low'],'max':v['high'],'overlaps':0,'unknowns':0});c['descriptor_states']+=1;c['min']=hex(min(int(c['min'],16),int(v['low'],16)));c['max']=hex(max(int(c['max'],16),int(v['high'],16)));c['overlaps']+=v['overlaps_queue'];c['unknowns']+=bool(v['unknown'])
for v in r['DMA_successors'].values():
 key=str(v['channel'])+':'+v['pointer'];node=links.setdefault(key,{'channel':v['channel'],'pointer':v['pointer'],'descriptor_states':0,'reads':0,'aligned':True,'descriptor_overlap':False,'next_destinations':set()});node['descriptor_states']+=1;node['reads']+=v['count'];node['aligned'] &=v['aligned'];node['descriptor_overlap'] |=v['descriptor_overlaps_queue'];node['next_destinations'].add(v['loaded_next_destination'])
for key in r['DMA']:
 ch,raw=key.split(':',1);td=struct.unpack(edma_sw.TCD_FMT,bytes.fromhex(raw));target=edma_sw.link_channel(td[6])
 if target is None or td[10]&16:continue
 mod=(td[1]>>3)&31;width=1<<(td[1]&7);count=edma_sw.iteration_count(td[9]);delta=count*((td[3]+width-1)//width)*td[7]+int.from_bytes(td[8].to_bytes(4,'big'),'big',signed=True)
 key='modulo ring' if mod else 'zero drift' if delta==0 else 'nonzero drift outside DDR' if not 0x40000000<=td[5]<0x80000000 else 'nonzero DDR drift';classes[key]+=1
 if key=='nonzero DDR drift' and len(drift)<12:drift.append({'channel':ch,'destination':hex(td[5]),'delta':delta})
for v in links.values():v['next_destinations']=sorted(v['next_destinations'])
rows=[]
for v in r['bulk_callers'].values():
 lo=int(v['min_destination'],16);hi=int(v['max_end'],16)
 if 0x40000000<=lo<=hi<0x48000000:rows.append({**v,'gap_below_queue':hex(0x47be2860-hi)})
rows.sort(key=lambda v:int(v['gap_below_queue'],16))
out={'PC_only':True,'passed':r['passed'],'runtime_ms':r['elapsed_model_ms'],'confirmed_pattern_replacement':r['pattern_replacement_confirmed'],'trace_path':'SoftwareBank native fast path explicitly disabled; actual _run plus SSI major-completion observations','executed_descriptor_counts':r['DMA_executions'],'unique_descriptor_states':len(r['DMA']),'successor_state_observations':len(r['DMA_successors']),'actual_software_links_followed':r['software_DMA_links_followed'],'software_transfer_refusals':r['software_DMA_refused'],'software_errors':r['software_DMA_errors'],'minor_link_targets':r['DMA_link_targets'],'minor_requests_not_executed_by_model':r['minor_links_ignored'],'non_ESG_minor_link_destination_classes':dict(classes),'nonzero_DDR_drift_examples':drift,'payload_destination_groups':groups,'successor_nodes':list(links.values()),'closest_observed_DDR_bulk_callers':rows[:10],'largest_observed_bulk_calls':sorted(r['bulk_callers'].values(),key=lambda v:v['max_bytes'],reverse=True)[:10],'bulk_callers_observed':len(r['bulk_callers']),'bulk_calls':r['bulk_calls'],'bulk_overlap':r['bulk_overlaps'],'guest_queue_writers':r['guest_writers'],'host_queue_writes':r['host_queue_writes'],'limits':['Concrete observed successors and linked target identities are resolved for this workload, not for arbitrary future reprogramming.','Minor requests are counted but not executed; all observed targets are self-links. Exact self-link request/reload/arbitration and physical effects remain unverified.','Observed non-ESG drift outside DDR is not a proof excluding every future 32-bit wrap or misconfiguration.','Native DMA engine is disabled for tracing; this is a changed PC execution path, not physical timing or bit-exact scheduling equivalence.']}
Path('outputs/Digitone-E04-PC-resident-successor-writer-summary.json').write_text(json.dumps(out,indent=2));print('successor nodes',len(links),'reads',sum(v['reads'] for v in links.values()),'classes',dict(classes),'closest',rows[:2])
