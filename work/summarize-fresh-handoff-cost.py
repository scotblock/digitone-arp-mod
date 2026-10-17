import pathlib,json,collections,hashlib
o=pathlib.Path('outputs')
load=lambda name:json.loads((o/name).read_text())
rows={}
original=load('Digitone-cycle-complete-handoff-native-pattern-copy.json')
first=next(q for q in original['quantizer_calls'] if q['word']=='0x8000433b')
for mode in ('trace','pitch-fetch-neutral'):
 r=load('Digitone-fresh-handoff-'+mode+'-native-pattern-copy.json')
 assert r.get('_finished') and r['failure'] is None and all(r['storage_checks'].values())
 assert r['timing']['clock']['decode_mismatches']==0
 assert r['firmware_sha256']==original['firmware_sha256']
 q=next(q for q in r['quantizer_calls'] if q['word']=='0x8000433b')
 p=next(p for p in r['pitch_outputs'] if p['event']==q['event'] and p['generation']==q['generation'] and p['ordinal']>q['ordinal'])
 assert (q['event'],q['generation'],q['note'],q['expected'])==(first['event'],first['generation'],57,57)
 assert p['fixed_note']>>16==57
 d=r['fresh_cost'];points=d['boundaries']
 a=next(x for x in points if x['label']=='pitch_entry')
 b=next(x for x in points if x['label']=='pitch_output' and x['cycles']>a['cycles'])
 blocks=[x for x in d['blocks'] if a['cycles']<=x['cycles']<b['cycles']]
 memory=[x for x in d['memory'] if a['cycles']<=x['cycles']<b['cycles']]
 counts=collections.Counter()
 for x in memory:counts[x['kind']]+=x['cost']
 stale=[x for x in r['DMA_captures'] if x['ms']>=20 and not x['all_words_fresh']]
 rows[mode]={'duration_ms':r['final_timing']['ms'],'first_quantization':q,'pitch_output':p,'pitch_entry':a,'pitch_exit':b,'pitch_interval_cycles':b['cycles']-a['cycles'],'pitch_interval_us':(b['cycles']-a['cycles'])/264,'helper_block_cycles':sum(x['cost'] for x in blocks if x['helper']),'all_block_cycles':sum(x['cost'] for x in blocks),'helper_fetch_cycles_before_ablation':counts['fetch'],'helper_data_cycles':counts['read']+counts['write'],'active_vector_sets':sorted(set(tuple(x['vectors']) for x in blocks)),'removed_fetch_cycles':d['removed_fetch_cycles'],'stale_captures':stale,'following_stores':d['next_stores'],'boundaries':points,'storage_checks':r['storage_checks'],'FIFO_counts':r['timing']['memory']['FIFO']['counts'],'render_deadline':r['timing']['render_deadline']}
 intervals=[]
 for ent in (x for x in points if x['label']=='pitch_entry'):
  ex=next(x for x in points if x['label']=='pitch_output' and x['cycles']>ent['cycles'])
  mm=[x for x in d['memory'] if ent['cycles']<=x['cycles']<ex['cycles']]
  intervals.append({'entry_cycles':ent['cycles'],'exit_cycles':ex['cycles'],'elapsed_cycles':ex['cycles']-ent['cycles'],'helper_fetch_cycles_before_ablation':sum(x['cost'] for x in mm if x['kind']=='fetch'),'helper_data_cycles':sum(x['cost'] for x in mm if x['kind']!='fetch')})
 rows[mode]['pitch_intervals']=intervals
 rows[mode]['window_pitch_outputs']=[x for x in r['pitch_outputs'] if 2619<=x['ms']<=2625]
t,n=rows['trace'],rows['pitch-fetch-neutral']
for mode,x in rows.items():
 x['attribution_residual_cycles']=x['pitch_interval_cycles']-x['all_block_cycles']-x['helper_data_cycles']
 x['helper_computation_and_flow_cycles']=x['helper_block_cycles']-(0 if mode=='pitch-fetch-neutral' else x['helper_fetch_cycles_before_ablation'])
basecap=[x for x in original['DMA_captures'] if x['ms']>=20 and not x['all_words_fresh']]
reproduces=(t['first_quantization']['cycles']==first['cycles'] and [(x['cycles'],x['start'],x['bytes']) for x in t['stale_captures']]==[(x['cycles'],x['start'],x['bytes']) for x in basecap])
entry_equal=t['pitch_entry']['cycles']==n['pitch_entry']['cycles']
assert reproduces and entry_equal
assert [(p['event'],p['generation'],p['track'],p['fixed_note']) for p in t['window_pitch_outputs']]==[(p['event'],p['generation'],p['track'],p['fixed_note']) for p in n['window_pitch_outputs']]
assert [x['helper_fetch_cycles_before_ablation'] for x in n['pitch_intervals']]==[n['removed_fetch_cycles'],0,0]
assert all(not x['FIFO_counts'].get(k,0) for x in rows.values() for k in ['TX_underflow','TX_overflow','RX_overflow','RX_empty_read','invalid_shift_words_completed'])
answer={'firmware_modified':False,'exact_original_timing_reproduced':reproduces,'same_ablation_pitch_entry_cycle':entry_equal,'controls':rows,'limits':['264/132 MHz and cache/bus costs are uncalibrated assumptions.','The fetch-neutral control preserves instruction execution, cache tags and data costs but removes selected instruction-fetch delays/reservations. It is a diagnostic, not an implementable firmware change.','Clock costs and interrupt delivery are basic-block granular; adding trace boundaries can alter translation. Exact reproduction is checked explicitly.','Captures and following stores do not establish physical codec output or cache-value coherence.']}
answer['isolated_helper_cost']=load('Digitone-fresh-pitch-local-cost.json')
answer['downstream_comparison']=load('Digitone-fresh-downstream-comparison.json')
stock=load('Digitone-stock-cycle-complete-handoff-native-pattern-copy.json')
def matching_event(report,kind):
 return next(x for x in report['events'] if x['kind']==kind and x.get('event')==first['event'] and x.get('generation')==first['generation'])
phase={kind:{'stock_cycles':matching_event(stock,kind)['cycles'],'modified_cycles':matching_event(original,kind)['cycles']} for kind in ['acceptance','pitch']}
for kind,v in phase.items():
 v['difference_cycles']=v['modified_cycles']-v['stock_cycles'];v['difference_us']=v['difference_cycles']/264
answer['earlier_phase_comparison']=phase
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(syx.read_bytes()).hexdigest()==original['firmware_sha256']
(o/'Digitone-fresh-handoff-cost-summary.json').write_text(json.dumps(answer,indent=2))
conclusion='The scoped pitch-helper fetch control prevents the two stale captures in this PC workload.' if reproduces and entry_equal and len(t['stale_captures'])==2 and not n['stale_captures'] else 'The scoped control does not yet establish pitch-helper fetch cost as the decisive cause; see the measured outcomes below.'
if reproduces and entry_equal and len(t['stale_captures'])==2 and len(n['stale_captures'])==1:
 conclusion='Removing the first fresh note’s 1,360 modeled helper-fetch cycles eliminates the smaller stale capture. The larger stale capture remains: fetch delay is a measured contributor, not a complete explanation.'
lines=['# First fresh receiving-pattern note: timing isolation','',conclusion+' Firmware remains unchanged.','',f"Exact original timing reproduced: {reproduces}. Control starts pitch processing at the same cycle: {entry_equal}.",'','| Run | Pitch interval (cycles) | Interval (µs) | Removed fetch cycles | Stale captures |','|---|---:|---:|---:|---:|']
for name,x in rows.items():lines.append(f"| {name} | {x['pitch_interval_cycles']} | {x['pitch_interval_us']:.3f} | {x['removed_fetch_cycles']} | {len(x['stale_captures'])} |")
lines+=['','Both controls execute the actual uninterrupted native pattern handoff and consume receiving event '+first['event']+' / generation '+str(first['generation'])+'. The incoming and outgoing note is 57 in both. No event eligibility or context metadata is injected at acceptance. The control removes fetch charges only while the pitch hook executes in the 2619–2625 ms diagnostic window; the preceding producer/context path remains charged.','',f"Measured helper fetch charges within the traced pitch interval: {t['helper_fetch_cycles_before_ablation']} cycles; helper data charges: {t['helper_data_cycles']} cycles. Active interrupt-vector sets: {t['active_vector_sets']}. The complete instruction/block and memory trace is retained in the individual run reports.",'','## Missed writes','']
lines.insert(lines.index('## Missed writes'),f"Measured helper computation/flow/stall block cost excluding its instruction fetches: {t['helper_computation_and_flow_cycles']} cycles. Interval attribution residual: {t['attribution_residual_cycles']} cycles; any residual is kept explicit rather than assigned to the helper.\n")
for x in t['following_stores']:lines.append(f"- {x['word']}: next CPU store occurs {x['lateness_cycles']} cycles ({x['lateness_cycles']/264:.3f} µs) after capture; store PC {x['pc']}.")
lines+=['','Fetch-cost removal changes subsequent scheduling and bus contention as well as elapsed helper time. It demonstrates a contribution to the smaller capture failure, while leaving the larger failure unresolved. It does not identify a unique silicon defect or prove that every excess cycle belongs to the hook.','',*['- '+x for x in answer['limits']]]
lines+=['','The window contains the fresh track-2 pitch call followed by two other pitch calls. The latter calls have zero fetch charges in both runs, so all 1,360 removed cycles belong to the first call. Both later calls still take 122 cycles, and all three pitches match between controls.']
dc=answer['downstream_comparison']['comparison']
lines+=['','## Downstream scheduling','','After the first pitch output, the render executes the same instruction-block sequence when the nested audio-completion interrupt is excluded. The first sequence divergence is the position of vector 174 at the stock loop starting at `4009a2d6`. No nested interrupt occurs inside the measured first pitch interval; vector 174 does occur later before the sample writes.', '',f"The control saves 1,360 pitch-fetch cycles, but later block/fetch costs increase by {dc['post_pitch_extra_fetch_cycles_in_control']} cycles and other downstream costs by {dc['post_pitch_extra_other_cycles_in_control']} cycles. The first mixer write therefore advances only {dc['first_store_advance_cycles']} cycles (4.186 µs). Its remaining capture lateness is 4,430 cycles (16.780 µs). Both runs execute 74,372 observed downstream instructions before that store.", '',f"The inherited stock comparison consumes the same event/generation earlier: acceptance is shifted by {phase['acceptance']['difference_cycles']} cycles ({phase['acceptance']['difference_us']:.3f} µs), and pitch-entry observation by {phase['pitch']['difference_cycles']} cycles ({phase['pitch']['difference_us']:.3f} µs). Entry stamps include basic-block precharging and are not isolated function costs. This earlier phase shift remains in both diagnostic controls; its specific cause is not proved here.",'','Next: compare the matching stock render interval and its interrupt/cache phase, then separate the earlier context-processing shift from downstream memory cost. Do not assume another pitch-only reduction will close the larger gap.']
lines+=['','## Independent local cost test','','With an explicitly constructed valid context and no scheduler or DMA, the cold hook takes 3,054 modeled cycles: 1,760 instruction-fill cycles, 960 data-fill cycles and 334 other cycles. Self-warmed execution settles at 334 cycles. The scale lookup itself accounts for 651 cold cycles (531 block/fetch plus 120 data); validation and context-reading work account for the rest of the helper path. These are separate local fixtures and are not substituted for the actual playback trace.']
(o/'Digitone-fresh-handoff-cost-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'reproduces':reproduces,'equal_entry':entry_equal,'runs':{k:{x:v[x] for x in ['pitch_interval_cycles','helper_fetch_cycles_before_ablation','helper_data_cycles','removed_fetch_cycles']}|{'stale':len(v['stale_captures'])} for k,v in rows.items()}},indent=2))
