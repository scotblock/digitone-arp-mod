import pathlib,json,collections,hashlib,sys,zlib,struct
o=pathlib.Path('outputs');read=lambda name:json.loads((o/name).read_text())
reports={k:read('Digitone-matched-render-'+k+'-native-pattern-copy.json') for k in ['stock','full']}
original=read('Digitone-fresh-handoff-trace-native-pattern-copy.json')
first=next(x for x in original['quantizer_calls'] if x['word']=='0x8000433b')
checkpoint=pathlib.Path('work/cache-fresh-trace-prepared.snap')
checkpoint_sha=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
from emu.harness import PAGE
saved=snapshot._load_blob(str(checkpoint))
def byte_at(addr):return zlib.decompress(saved['pages'][addr//PAGE*PAGE])[addr%PAGE]
roots={hex(b):[[byte_at(b+t*0x3d0+0x3cb),struct.unpack('b',bytes([byte_at(b+t*0x3d0+0x3ce)]))[0]] for t in range(4)] for b in [0x407c61e9,0x407b00cc]}
assert roots=={'0x407c61e9':[[61,0]]*4,'0x407b00cc':[[59,5]]*4}
measurements={};segments={}
for mode,r in reports.items():
 assert r.get('_finished') and r['failure'] is None and all(r['storage_checks'].values())
 assert r['prepared_checkpoint']['sha256']==checkpoint_sha
 assert r['timing']['clock']['decode_mismatches']==0 and not r['helper_reinjected']
 assert r['PC_runtime_extension_installed'] is False
 # The initial stock run preceded the added report-only root descriptor.
 # Validate both actual pattern hashes before correcting that legacy label.
 for label in ['initial','after actual transition']:
  a=next(m for m in r['marks'] if m['label']==label)
  b=next(m for m in reports['full']['marks'] if m['label']==label)
  assert a['backing_hash']==b['backing_hash']
 if mode=='stock' and 'loaded_root_scale' not in r:
  r['legacy_pre_selection_root_descriptor']=r['root_scale_fixture']
  r['root_scale_fixture']=dict(reports['full']['root_scale_fixture'])
  r['loaded_root_scale']=roots
  r['root_descriptor_correction']='Derived from the shared snapshot and verified matching source/receiving pattern hashes; report-only correction, no guest changes.'
  (o/'Digitone-matched-render-stock-native-pattern-copy.json').write_text(json.dumps(r,indent=2))
 p=r['matched_probe'];ev=next(e for e in r['events'] if e['kind']=='pitch' and e.get('event')==first['event'] and e.get('generation')==first['generation'])
 pitch=next(e for e in p['points'] if e['label']=='pitch_entry' and e['cycles']==ev['cycles'])
 fr=next(f for f in pitch['frames'] if f[0]==191);start=fr[1]
 body=next(e for e in p['points'] if e['label']=='render_body_entry' and any(f[0]==191 and f[1]==start for f in e['frames']))
 store=next(e for e in p['stores'] if e['pc']=='0x40096c26' and e['cycles']>pitch['cycles'] and any(f[0]==191 and f[1]==start for f in e['frames']))
 end=next(e for e in p['interrupts'] if e['kind']=='exit' and e['vector']==191 and e['frames'][-1][1]==start)
 blocks=[e for e in p['blocks'] if start<=e['cycles']<store['cycles'] and e['instructions']]
 data=[e for e in p['data'] if start<=e['cycles']<store['cycles']]
 entries=[e for e in p['interrupts'] if e['kind']=='entry' and e['taken'] and not e['from_instruction'] and start<=e['cycle_before']<store['cycles']]
 irq_entry=sum(e['cycles']-e['cycle_before'] for e in entries)
 capture=next(e for e in p['captures'] if e['start']==store['address'] and e['cycles']>start)
 direct_pitch=next(e for e in r['pitch_outputs'] if e['event']==first['event'] and e['generation']==first['generation'])
 assert direct_pitch['fixed_note']>>16==57
 cost=collections.Counter()
 for e in data:cost.update(e['charges'])
 elapsed=store['cycles']-start;blockcost=sum(e['cost'] for e in blocks);datacost=sum(e['cost'] for e in data)
 measurements[mode]={'event':ev['event'],'generation':ev['generation'],'frame_start_cycles':start,'frame_end_cycles':end['cycles'],'body_entry_cycles':body['cycles'],'pitch_entry_cycles':pitch['cycles'],'pitch_fields':pitch['fields'],'first_store':store,'first_capture':capture,'first_store_elapsed_cycles':elapsed,'frame_wall_cycles':end['cycles']-start,'block_cycles':blockcost,'fetch_cycles':sum(e['fetch_cycles'] for e in blocks),'data_cycles':datacost,'data_charge_breakdown':dict(cost),'IRQ_entry_cycles':irq_entry,'attribution_residual_cycles':elapsed-blockcost-datacost-irq_entry,'instructions':sum(e['instructions'] for e in blocks),'fresh_margin_cycles':capture['cycles']-store['cycles'],'all_workload_stale_captures':sum(not e['all_words_fresh'] for e in r['DMA_captures'] if e['ms']>=20),'render_PC_sequence':[e['pc'] for e in blocks if e['frames'] and e['frames'][-1][0]==191 and not 0x47be0000<=int(e['pc'],16)<0x47be0000+2564]}
 segments[mode]={'blocks':blocks,'data':data}
s,f=measurements['stock'],measurements['full']
assert s['pitch_fields']==f['pitch_fields']
for mode,seg in segments.items():
 h=[b for b in seg['blocks'] if 0x47be0000<=int(b['pc'],16)<0x47be0000+2564]
 measurements[mode]['overlay_fetch_cycles']=sum(b['fetch_cycles'] for b in h)
 measurements[mode]['overlay_block_cycles']=sum(b['cost'] for b in h)
 measurements[mode]['overlay_instructions']=sum(b['instructions'] for b in h)
 assert reports[mode]['timing']['memory']['costs']==reports['full']['timing']['memory']['costs']
 assert all(not reports[mode]['timing']['memory']['FIFO']['counts'].get(k,0) for k in ['TX_underflow','TX_overflow','RX_overflow','RX_empty_read','invalid_shift_words_completed'])
delta={k:f[k]-s[k] for k in ['frame_start_cycles','body_entry_cycles','pitch_entry_cycles','first_store_elapsed_cycles','frame_wall_cycles','block_cycles','fetch_cycles','data_cycles','IRQ_entry_cycles','attribution_residual_cycles','instructions']}
delta['first_store_cycles']=f['first_store']['cycles']-s['first_store']['cycles']
assert delta['first_store_cycles']==delta['frame_start_cycles']+delta['first_store_elapsed_cycles']
delta['computation_flow_and_stall_cycles']=delta['block_cycles']-delta['fetch_cycles']
delta['data_charge_breakdown']={k:f['data_charge_breakdown'].get(k,0)-s['data_charge_breakdown'].get(k,0) for k in set(f['data_charge_breakdown'])|set(s['data_charge_breakdown'])}
delta['overlay_fetch_cycles']=f['overlay_fetch_cycles']-s['overlay_fetch_cycles']
delta['stock_region_fetch_cycles']=delta['fetch_cycles']-delta['overlay_fetch_cycles']
baseline_stale=[(x['cycles'],x['start']) for x in original['DMA_captures'] if x['ms']>=20 and not x['all_words_fresh']]
replayed_stale=[(x['cycles'],x['start']) for x in reports['full']['DMA_captures'] if x['ms']>=20 and not x['all_words_fresh']]
exact_full_reproduction=reports['full']['quantizer_calls'][0]['cycles']==first['cycles'] and baseline_stale==replayed_stale
assert exact_full_reproduction
counts={}
for mode,seg in segments.items():
 cc=collections.Counter()
 for b in seg['blocks']:cc[b['pc']]+=b['fetch_cycles']
 counts[mode]=cc
hot=sorted(({'pc':pc,'stock_fetch_cycles':counts['stock'][pc],'full_fetch_cycles':counts['full'][pc],'delta':counts['full'][pc]-counts['stock'][pc]} for pc in set(counts['stock'])|set(counts['full'])),key=lambda x:x['delta'],reverse=True)[:20]
phase=read('Digitone-prepared-timer-phase-audit.json')
result={'firmware_modified':False,'shared_checkpoint_sha256':checkpoint_sha,'initial_roots':roots,'exact_previous_full_reproduction':exact_full_reproduction,'measurements':measurements,'full_minus_stock':delta,'largest_fetch_differences':hot,'prepared_timer_audit':phase,'limits':['264/132 MHz, 48 kHz audio and memory costs remain assumptions.','One shared prepared guest state; stock control restores seven hook sites while retaining unused helper RAM. This isolates runtime instruction changes, not a fresh physical stock boot.','Cycle costs and write observations are basic-block granular; costs are observational intervals, not silicon measurements.','First buffer address may differ between logically matching render blocks; capture comparisons use the first write target belonging to each matched frame.','Any accounting residual is retained explicitly.']}
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(syx.read_bytes()).hexdigest()==reports['full']['firmware_sha256']==reports['stock']['firmware_sha256']
for m in measurements.values():m.pop('render_PC_sequence')
(o/'Digitone-matched-render-comparison.json').write_text(json.dumps(result,indent=2))
lines=['# Matching stock and prototype render: phase versus cost','','Both runs restore the same prepared guest snapshot, use the same workload and disable HLE. The stock control restores all seven hook sites. The prototype reproduces the preceding diagnostic exactly. Firmware remains unchanged.','','The older comparison used different preparation end times. The raw timer “now” difference is 42,666 ticks at 64 MHz (0.666656 ms); the standard timed restore rescales this phase by 264/64 with an unchanged 132 MHz bus, giving 175,997.25 core cycles. The new pair removes that starting-state confound.','','| Measurement | Stock | Prototype | Difference |','|---|---:|---:|---:|']
for key,label in [('frame_start_cycles','Matched render start (cycles)'),('first_store_elapsed_cycles','Render start → first output write (cycles)'),('fetch_cycles','Instruction fetch charges (cycles)'),('data_cycles','Data memory charges (cycles)'),('IRQ_entry_cycles','Nested interrupt entry charges (cycles)'),('attribution_residual_cycles','Explicit accounting residual (cycles)'),('all_workload_stale_captures','Stale captures after 20 ms')]:
 lines.append(f"| {label} | {s[key]} | {f[key]} | {f[key]-s[key]} |")
lines+=['',f"The first output write moves by {delta['first_store_cycles']:,} cycles. This separates exactly into a {delta['frame_start_cycles']:,}-cycle render-start shift plus {delta['first_store_elapsed_cycles']:,} cycles of additional elapsed work after that start. The within-render difference comprises {delta['fetch_cycles']:,} instruction-fetch cycles, {delta['data_cycles']:,} data-memory cycles, {delta['computation_flow_and_stall_cycles']:,} computation/flow/stall block cycles, {delta['IRQ_entry_cycles']:,} nested interrupt-entry cycles and {delta['attribution_residual_cycles']:,} explicitly unassigned cycles.",'',f"Both runs consume event {first['event']} / generation {first['generation']} and output note 57. The first output buffers are {s['first_store']['address']} and {f['first_store']['address']}; each is matched to its own render frame and first subsequent DMA capture. Observed write margins are {s['fresh_margin_cycles']/264:.3f} µs (stock) and {f['fresh_margin_cycles']/264:.3f} µs (prototype). Positive margin alone does not prove every sample is fresh; the capture freshness flags and full-workload counts are preserved in the summary.",'','## Limits','',*['- '+x for x in result['limits']]]
lines.insert(lines.index('## Limits'),f"The complete 72-byte event at pitch entry is identical in both runs. Overlay-RAM instruction fetches account for {delta['overlay_fetch_cycles']:,} added cycles; fetch charges outside that overlay rise by a further {delta['stock_region_fetch_cycles']:,} cycles. Overlay code also executes displaced stock instructions, so region totals are not a count of purely new work. Fetch, data, flow and stall costs remain distinct.\n")
lines.insert(lines.index('## Limits'),'The earlier roughly 2 ms pitch-entry shift does not survive the shared-start comparison: matched render starts differ by one cycle. The remaining observed regression is work within the render, including the broader context hooks and downstream memory effects. The preceding fetch-neutral control isolated 1,360 pitch-fetch cycles and removed one capture; optimizing only that pitch fetch path does not address the entire 6,685-cycle within-render difference.\n')
lines+=['','Next: reduce the combined context/pitch hot path’s instruction footprint while preserving its validations, then rerun this shared-state pair. Fetch charges dominate the measured difference, but this accounting does not uniquely assign every downstream miss to one helper or certify physical timing.']
(o/'Digitone-matched-render-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'delta':delta,'stock_stale':s['all_workload_stale_captures'],'full_stale':f['all_workload_stale_captures'],'stock_margin':s['fresh_margin_cycles'],'full_margin':f['fresh_margin_cycles']},indent=2))
