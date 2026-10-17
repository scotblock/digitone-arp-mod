import pathlib,json,hashlib
O=pathlib.Path('outputs')
names=['prefix-stock','prefix-sham','prefix-pitch-only','prefix-fixed','prefix-full','prefix-context-only','prefix-memory-neutral','prefix-compute-neutral','prefix-fetch-neutral','long-stock','long-fixed','long-full']
rows=[];cases={};snapshot=None
fault_keys=['TX_underflow','TX_overflow','RX_overflow','RX_empty_read','invalid_shift_words_completed']
for name in names:
 r=json.loads((O/f'Digitone-compact-hook-timing-{name}.json').read_text());q=r['runs'][0];cases[name]=q
 assert r['failure'] is None and q['halted'] is None and q['clock']['decode_mismatches']==0
 assert r['firmware_before']==r['firmware_after']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
 assert all(q['storage_checks'].values()) and not q['startup_provenance']['helper_and_header_reinjected']
 h=q['startup_provenance']['snapshot_sha256'];snapshot=snapshot or h;assert snapshot==h
 assert q['DMA_summary']['final_clock_timer_gap_cycles']==0
 assert len(q['table_reads'])==len(q['quantizer_calls'])
 for call in q['quantizer_calls']:
  output=next(x for x in q['diagnostic_pitch_controls'] if x['cycles']>=call['cycles'])
  assert output['computed_fixed']==call['expected']<<16
 old=json.loads((O/f'Digitone-loader-timing-{name}.json').read_text())['runs'][0]
 rows.append({'case':name,'ms':q['ms'],'DMA':q['DMA_summary'],'render':q['render_deadline'],'FIFO_faults':sum(q['memory_model']['FIFO']['counts'].get(k,0) for k in fault_keys),'storage_checks':q['storage_checks'],'quantizer_calls':len(q['quantizer_calls']),'pitch_sequence':[(x['track'],x['delivered_fixed']//65536) for x in q['diagnostic_pitch_controls']],'previous_DMA':old['DMA_summary']})
assert next(x for x in rows if x['case']=='prefix-fixed')['pitch_sequence']==next(x for x in rows if x['case']=='prefix-stock')['pitch_sequence']
assert next(x for x in rows if x['case']=='prefix-full')['pitch_sequence']==next(x for x in rows if x['case']=='prefix-pitch-only')['pitch_sequence']
q=cases['prefix-full'];a=next(x for x in q['checkpoints'] if x['label']=='pitch_entry');b=next(x for x in q['checkpoints'] if x['label']=='pitch_output')
first={'cycles':b['cycles']-a['cycles'],'instructions':b['instructions']-a['instructions'],'fetch_stall_cycles':b['memory_counts']['instruction_fill_stall_cycles']-a['memory_counts']['instruction_fill_stall_cycles']}
traced_old=json.loads((O/'Digitone-loader-timing-prefix-full-traced.json').read_text())['runs'][0]
window_cost={}
for name,run in [('previous',traced_old),('compact',q)]:
 blocks=[x for x in run['block_costs'] if x['helper']]
 window_cost[name]={'window_ms':[70,80],'instructions':sum(x['instructions'] for x in blocks),'charged_cycles':sum(x['charged_cycles'] for x in blocks),'blocks':len(blocks)}
old_summary=json.loads((O/'Digitone-loader-timing-summary.json').read_text())
old_stock=json.loads((O/'Digitone-loader-timing-prefix-stock.json').read_text())['runs'][0]
stock_repeat={key:cases['prefix-stock'][key]==old_stock[key] for key in ['DMA_summary','DMA_captures','diagnostic_pitch_controls','render_deadline','transport_trace']}
assert all(stock_repeat.values())
build=json.loads(pathlib.Path('work/compact-hook-build.json').read_text())
startup=json.loads((O/'Digitone-compact-hook-startup-playback.json').read_text());assert startup['passed']
helpers=json.loads((O/'Digitone-compact-hook-helper-checks.json').read_text())
pitch=json.loads((O/'Digitone-compact-hook-pitch-differential.json').read_text())
abi=json.loads((O/'Digitone-compact-hook-ABI.json').read_text());assert abi['failure'] is None
limits=old_summary['limits']
out={'firmware_modified':False,'all_runs_completed':True,'all_cases_meet_sample_freshness':all(x['DMA']['captures_with_unfresh_words']==x['DMA']['late']==x['DMA']['unresolved']==0 for x in rows),'all_cases_meet_FIFO_model':all(x['FIFO_faults']==0 for x in rows),'snapshot_sha256':snapshot,'build':build,'startup_passed':True,'native_checks':{'resolver_read_differential':helpers['resolver_and_read_differential_cases'],'pitch_differential':pitch['count'],'hook_tracks':len(abi['cases']),'quantizer_samples':abi['quantizer_comparisons']},'first_pitch':first,'previous_first_pitch':old_summary['first_pitch'],'assumptions':old_summary['assumptions'],'cases':rows,'limits':limits}
(O/'Digitone-compact-hook-timing-summary.json').write_text(json.dumps(out,indent=2))
out['traced_window_helper_cost']=window_cost
out['stock_short_repeat_matches_previous']=stock_repeat
(O/'Digitone-compact-hook-timing-summary.json').write_text(json.dumps(out,indent=2))
passed=out['all_cases_meet_sample_freshness'] and out['all_cases_meet_FIFO_model']
lines=['# Digitone OS 1.42: compact hook timing controls','',f'The compact PC-only overlay completed all twelve controls. Sample freshness and FIFO checks {"pass" if passed else "do not all pass"} under the same assumed clock and memory costs. The original firmware remains unchanged; no installable firmware was generated.','', '## Change and native validation','', 'The resolver saves its scratch register once across the four header comparisons. The pitch helper removes two scratch-register saves whose values are overwritten before use. Internal branches use shorter encodings where they fit. All entry addresses, validation checks, table bytes and startup/copy layout are retained. Unused bytes are unreachable padding, so the whole copied overlay remains 2,324 bytes.','', '| Helper | Previous body bytes | Compact body bytes |','|---|---:|---:|']
for c in build['changes']:lines.append(f'| {c["helper"]} | {c["previous_bytes"]} | {c["compact_bytes"]} |')
lines+=['', 'Native differential tests cover 72 resolver/read cases and 72 pitch cases across four tracks, including invalid context and event/cache predicates. All compared registers, materialized condition flags and event/record contents match the prior code. The actual displaced stock hook instructions also pass the four-track ABI checks, plus 162 sampled quantizer checks. The quantizer itself was unchanged.','', 'The compact code passed a fresh actual loader-to-application run, initialization and playback. Timing runs use that new loader-derived settled snapshot and the matching ephemeral flash contents. Full/fixed cases retain installed hooks and metadata rather than reinjecting them.','', '## Timing results','', '| Control | Duration ms | Stale captures | Previous stale captures | Minimum margin µs | Render period overruns | FIFO faults |','|---|---:|---:|---:|---:|---:|---:|']
for x in rows:lines.append(f'| {x["case"]} | {x["ms"]:.3f} | {x["DMA"]["captures_with_unfresh_words"]} | {x["previous_DMA"]["captures_with_unfresh_words"]} | {x["DMA"]["minimum_margin_us"]:.3f} | {x["render"]["late"]} | {x["FIFO_faults"]} |')
lines+=['',f'The first pitch-hook execution falls from {old_summary["first_pitch"]["instructions"]} to {first["instructions"]} instructions, from {old_summary["first_pitch"]["cycles"]} to {first["cycles"]} modeled cycles, and from {old_summary["first_pitch"]["fetch_stall_cycles"]} to {first["fetch_stall_cycles"]} instruction-fetch stall cycles. The full/fixed short-run margin improves from −2.227 µs to {cases["prefix-full"]["DMA_summary"]["minimum_margin_us"]:.3f} µs. Context helpers also benefit from the smaller resolver.','', 'The fixed-pitch control runs the helper but restores the original note. Its short pitch sequence matches stock-path playback; the full overlay matches the pitch-only control. Neutral-cost controls are diagnostic counterfactuals. Render-handler period overruns remain a separate metric from sample freshness and FIFO faults.','', 'All runs have zero timing decoder mismatches, no halt, zero final core/timer gap, intact helper/table/guards and no unexpected guest writes to the watched reserved region. Every observed quantizer output matches the oracle and reads the copied table.','', '## Limits and next step','', 'These observations depend on a 264 MHz core, 132 MHz bus, 48 kHz audio and assumed fill/writeback/beat costs of 40/32/8 cycles. The positive minimum margin is narrow. Finite tests do not establish physical timing, cache coherence or exclusive RAM ownership.','', *['- '+x for x in limits], '', 'Next: seek more timing margin in the repeated context path and test heavier sustained-note/pattern-transition workloads. The cached-context producer fixture and physical cache/coherence questions still need resolution before treating this as hardware-ready.']
(O/'Digitone-compact-hook-timing-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'freshness':out['all_cases_meet_sample_freshness'],'FIFO':out['all_cases_meet_FIFO_model'],'first_pitch':first,'rows':[{'case':x['case'],'stale':x['DMA']['captures_with_unfresh_words'],'margin_us':x['DMA']['minimum_margin_us']} for x in rows]},indent=2))
