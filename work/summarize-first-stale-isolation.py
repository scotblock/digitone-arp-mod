"""Causal controls for the observed PC-only first stale payload read."""
import pathlib,json,hashlib,collections
O=pathlib.Path('outputs')
names=['stock','sham','stock_changed','all_fixed','full','memory-neutral','compute-neutral','context-only','stock-trace','fixed-trace','pitch-fetch-neutral']
source={};rows=[]
for name in names:
 r=json.loads((O/f'Digitone-first-stale-{name}.json').read_text());q=r['runs'][0];source[name]=q
 assert r['failure'] is None and q['halted'] is None
 assert r['firmware_before']==r['firmware_after']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
 assert q['clock']['decode_mismatches']==0 and q['DMA_summary']['final_clock_timer_gap_cycles']==0
 assert 80<=q['ms']<81
 target=min((x for x in q['DMA_captures'] if x['start']=='0x80001b00'),key=lambda x:abs(x['cycles']-16722874))
 rows.append({'case':name,'emulated_ms':q['ms'],'freshness':q['DMA_summary'],'first_target_read':target,
              'delivered_pitch_sequence':[(x['track'],x['delivered_fixed']//65536) for x in q['diagnostic_pitch_controls']],
              'ablation':q.get('cost_ablation'),'pitch_fetch_ablation':q.get('pitch_fetch_ablation'),
              'handler_occupancy':q['render_deadline']})
by={x['case']:x for x in rows}
assert by['all_fixed']['delivered_pitch_sequence']==by['stock']['delivered_pitch_sequence']
assert by['stock_changed']['delivered_pitch_sequence']==by['full']['delivered_pitch_sequence']
assert by['stock']['freshness']['late']==by['stock_changed']['freshness']['late']==by['sham']['freshness']['late']==0
assert by['full']['freshness']['late']==by['all_fixed']['freshness']['late']==1
assert by['full']['first_target_read']['cycles']==by['all_fixed']['first_target_read']['cycles']==16722874
assert by['full']['first_target_read']['next_completion_cycles']==by['all_fixed']['first_target_read']['next_completion_cycles']==16723029
for name in ['memory-neutral','compute-neutral','context-only','pitch-fetch-neutral']:
 assert by[name]['freshness']['late']==0 and by[name]['freshness']['captures_with_unfresh_words']==0
full=source['full'];a=next(x for x in full['checkpoints'] if x['label']=='pitch_entry');b=next(x for x in full['checkpoints'] if x['label']=='pitch_output')
blocks=[x for x in full['block_costs'] if a['cycles']<=x['cycles']<b['cycles']]
assert set(tuple(x['active_vectors']) for x in blocks)=={(191,)}
counts={k:b['memory_counts'].get(k,0)-a['memory_counts'].get(k,0) for k in b['memory_counts']}
pitch={'entry_cycles':a['cycles'],'output_cycles':b['cycles'],'elapsed_cycles':b['cycles']-a['cycles'],
       'elapsed_us':(b['cycles']-a['cycles'])/264,'instructions':b['instructions']-a['instructions'],
       'instruction_fetch_cycles':counts['instruction_fill_stall_cycles'],
       'data_fill_cycles':counts['data_fill_stall_cycles'],'dirty_eviction_cycles':counts['dirty_eviction_stall_cycles'],
       'block_compute_and_flow_cycles':sum(x['compute_cycles_before_ablation'] for x in blocks),
       'helper_RAM_compute_cycles':sum(x['compute_cycles_before_ablation'] for x in blocks if x['helper']),
       'helper_RAM_fetch_cycles':sum(x['fetch_stall_cycles_before_ablation'] for x in blocks if x['helper']),
       'stock_code_compute_cycles':sum(x['compute_cycles_before_ablation'] for x in blocks if not x['helper']),
       'stock_code_fetch_cycles':sum(x['fetch_stall_cycles_before_ablation'] for x in blocks if not x['helper']),
       'scale_membership_routine':'0x40106b6c','scale_membership_calls':sum(x['pc']=='0x40106b6c' for x in blocks),
       'preemption_observed_in_interval':False}
assert pitch['elapsed_cycles']==pitch['instruction_fetch_cycles']+pitch['data_fill_cycles']+pitch['dirty_eviction_cycles']+pitch['block_compute_and_flow_cycles']
stock_state=next(x for x in source['stock-trace']['transport_trace'] if x.get('value')=='0x1')
fixed_state=next(x for x in source['fixed-trace']['transport_trace'] if x.get('value')=='0x1')
stock_accept=next(x for x in source['stock-trace']['checkpoints'] if x['label']=='acceptance')
fixed_accept=next(x for x in source['fixed-trace']['checkpoints'] if x['label']=='acceptance')
fetch_accept=next(x for x in source['pitch-fetch-neutral']['checkpoints'] if x['label']=='acceptance')
assert fetch_accept['cycles']==fixed_accept['cycles']
phase={'transport_state_writer':'0x400937c2','transport_state_address':'0x41342144',
       'stock_state_write':stock_state,'full_fixed_state_write':fixed_state,
       'state_write_difference_us':(fixed_state['cycles']-stock_state['cycles'])/264,
       'stock_first_acceptance':stock_accept,'full_fixed_first_acceptance':fixed_accept,
       'acceptance_difference_us':(fixed_accept['cycles']-stock_accept['cycles'])/264,
       'audio_block_period_us':176000/264,'targeted_fetch_control_keeps_acceptance_phase':True}
summary={'firmware_modified':False,'core_hz_candidate':264000000,'bus_hz_candidate':132000000,
         'memory_costs_assumed':{'fill':40,'writeback':32,'beat':8},'cases':rows,'pitch_path_costs':pitch,'scheduling':phase,
         'conclusions':['Changed coarse pitch is neither necessary nor sufficient for this stale read in the tested prefix.',
         'A stock-instruction pitch detour alone does not reproduce it.',
         'Context hooks shift transport state and note acceptance timing; context-only remains fresh with 11.55 us of margin at the target read.',
         'The full pitch-processing path then exhausts that margin. Instruction-fetch delay is a decisive modeled contributor: removing helper fetch delay from first pitch entry onward preserves earlier phase yet prevents the miss.',
         'Both helper compute and memory-delay ablations prevent the miss; their contributions interact through scheduling and cache/bus state, so they cannot be treated as additive hardware measurements.'],
         'limitations':['PC-only timing model with assumed clocks/costs, basic-block accounting and word-level DMA; not a measured hardware fault.',
         'Zero-cost memory/compute/fetch ablations are diagnostic counterfactuals, not implementable firmware fixes.',
         'Cache tags and dirty-state updates remain in memory/fetch-neutral cases; charge and bus-reservation effects are removed.',
         'Valid metadata is explicitly injected at commit for this cached-arp timing fixture; natural cached-context capture remains unproven.',
         'The controls isolate this first read over the exact first 80 ms; they do not certify later workloads, boot, storage ownership or physical cache coherence.']}
(O/'Digitone-first-stale-cause-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
display=['stock','sham','stock_changed','all_fixed','full','context-only','memory-neutral','compute-neutral','pitch-fetch-neutral']
labels={'stock':'Stock','sham':'Stock-instruction detour','stock_changed':'Stock + changed pitch','all_fixed':'Full hooks + stock pitch','full':'Full hooks + changed pitch','context-only':'Context hooks; stock pitch path','memory-neutral':'Full hooks; helper memory costs removed','compute-neutral':'Full hooks; helper computation costs removed','pitch-fetch-neutral':'Full hooks; helper fetch delays removed after first pitch entry'}
lines=['# Digitone OS 1.42: first stale read isolation','',
 'The changed pitch is excluded as the cause of this first stale read in the PC model. Full helper execution reproduces it even when the outgoing pitch is restored to stock. The failure is a combined timing effect: context hooks shift scheduling, then the first pitch-processing path exhausts the remaining sample-write margin. Modeled instruction-fetch delay is a decisive contributor. Firmware remains unchanged.','',
 '## Controls','',
 'Every case replays the same first 80 ms of the previous workload: initial 10 ms, pattern-2 request, PLAY press/release, then playback through 80 ms. The first stale read precedes the later keyboard-heavy section. Assumptions remain 264/132 MHz, 48 kHz audio, and fill/writeback/beat costs of 40/32/8 cycles. Original source bytes are unchanged; modifications and diagnostic fixtures exist only in guest RAM.','',
 '| Case | Stale reads | Minimum observed write margin (µs) | Margin at the previously failing stereo read (µs) |',
 '|---|---:|---:|---:|']
for name in display:
 r=by[name];lines.append(f'| {labels[name]} | {r["freshness"]["captures_with_unfresh_words"]} | {r["freshness"]["minimum_margin_us"]:.3f} | {r["first_target_read"]["completion_margin_us"]:.3f} |')
lines+=['',
 'Stock + changed pitch delivers the same first three coarse pitches as the full modified case. Full hooks + stock pitch delivers the stock sequence. These reciprocal controls show that changing 57 to 56 does not cause the miss, while restoring 57 does not remove it. The full and fixed-pitch controls reproduce the same capture and following-store cycles.','',
 'The previously failing 8-byte stereo read covers SRAM 0x80001b00–0x80001b07. The capture observer records core cycle 16,722,874 and the next final-word store at 16,723,029: 155 cycles (0.587 µs) later. Its timer-derived log time is 63.333784 ms; the corresponding core-clock observation is 63.344220 ms. Timer stamps can lag inside a basic block, so cycle comparisons are used for margins.','',
 '## Scheduling and cost attribution','',
 f'The native transport-state write at 0x400937c2 occurs {phase["state_write_difference_us"]:.3f} µs later with full hooks than stock. First note acceptance moves from core cycle {stock_accept["cycles"]:,} to {fixed_accept["cycles"]:,}, a {phase["acceptance_difference_us"]:.3f} µs shift, approximately one 666.667 µs audio block. Context-only has the same acceptance phase as full hooks, but its target read remains fresh by 11.545 µs. Adding the pitch path moves the following store 3,207 cycles (12.148 µs) later and produces the miss.','',
 'The first pitch-entry-to-output interval is 2,758 modeled cycles (10.447 µs), covering 370 instructions:','',
 f'- Instruction-fetch charges: {pitch["instruction_fetch_cycles"]:,} cycles (7.424 µs); {pitch["helper_RAM_fetch_cycles"]:,} are in helper RAM and {pitch["stock_code_fetch_cycles"]:,} in called stock code and the continuation.',
 '- Data fill and dirty eviction: 40 + 32 cycles.',
 '- Block computation, stalls and flow: 726 cycles; 500 in helper RAM and 226 in stock code.',
 '- The quantizer calls the existing scale-membership routine at 0x40106b6c three times. No nested interrupt appears within the measured pitch interval.',
 '',
 'This interval accounts for the pitch path itself; the larger difference at the sample store also includes downstream cache/bus and scheduling effects. The components are not interchangeable or simply additive across counterfactual runs.','',
 'The targeted fetch control removes helper instruction-fetch delays only from the first pitch entry onward. It leaves the earlier context-hook scheduling shift and the exact first acceptance cycle intact, while preserving cache tag/dirty-state updates. The target read becomes fresh by 8.133 µs. This directly ties the failure to instruction-fetch timing on the critical path rather than to pitch value or earlier phase shift alone. Removing all helper memory delays or helper computation costs also prevents the miss.','',
 '## Limits and next step','',*['- '+x for x in summary['limitations']], '',
 'Next: reduce and bound the first-note pitch path’s instruction footprint and repeated scale-membership work in the PC prototype, then rerun the same stock/fixed-pitch controls and longer active playback. Merely warming a cache for free is not a valid implementation. Physical timing costs still require independent evidence.']
(O/'Digitone-first-stale-cause-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'pitch_path':pitch,'state_shift_us':phase['state_write_difference_us'],'acceptance_shift_us':phase['acceptance_difference_us'],'cases':[{k:r[k] for k in ['case','delivered_pitch_sequence']}|{'stale':r['freshness']['late'],'target_margin_us':r['first_target_read']['completion_margin_us']} for r in rows]},indent=2))
