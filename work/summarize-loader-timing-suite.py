"""Summarize finite timing observations; a completed run need not meet deadlines."""
import pathlib,json,hashlib
O=pathlib.Path('outputs')
names=['prefix-stock','prefix-sham','prefix-pitch-only','prefix-fixed','prefix-full','prefix-context-only','prefix-memory-neutral','prefix-compute-neutral','prefix-fetch-neutral','long-stock','long-fixed','long-full']
rows=[];cases={};snapshot_hash=None
fault_keys=['TX_underflow','TX_overflow','RX_overflow','RX_empty_read','invalid_shift_words_completed']
for name in names:
 r=json.loads((O/f'Digitone-loader-timing-{name}.json').read_text());q=r['runs'][0];cases[name]=q
 assert r['failure'] is None and q['halted'] is None and q['clock']['decode_mismatches']==0
 assert r['firmware_before']==r['firmware_after']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
 assert all(q['storage_checks'].values()) and not q['startup_provenance']['helper_and_header_reinjected']
 h=q['startup_provenance']['snapshot_sha256'];snapshot_hash=snapshot_hash or h;assert snapshot_hash==h
 assert q['DMA_summary']['final_clock_timer_gap_cycles']==0
 assert len(q['table_reads'])==len(q['quantizer_calls'])
 for call in q['quantizer_calls']:
  output=next(x for x in q['diagnostic_pitch_controls'] if x['cycles']>=call['cycles'])
  assert output['computed_fixed']==call['expected']<<16,(name,call,output)
 fifo=q['memory_model']['FIFO']['counts'];faults=sum(fifo.get(k,0) for k in fault_keys)
 rows.append({'case':name,'ms':q['ms'],'DMA':q['DMA_summary'],'render':q['render_deadline'],'FIFO_faults':faults,'storage_checks':q['storage_checks'],'quantizer_calls':len(q['quantizer_calls']),'table_reads':len(q['table_reads']),'elapsed_seconds':r['elapsed_seconds'],'pitch_sequence':[(x['track'],x['delivered_fixed']//65536) for x in q['diagnostic_pitch_controls']],'cost_ablation':q['cost_ablation'],'pitch_fetch_ablation':q['pitch_fetch_ablation']})
traced=json.loads((O/'Digitone-loader-timing-prefix-full-traced.json').read_text());t=traced['runs'][0]
assert traced['failure'] is None and t['DMA_summary']==cases['prefix-full']['DMA_summary']
assert t['diagnostic_pitch_controls']==cases['prefix-full']['diagnostic_pitch_controls']
assert t['checkpoints'] and t['quantizer_calls']
start=next(x for x in t['checkpoints'] if x['label']=='pitch_entry');end=next(x for x in t['checkpoints'] if x['label']=='pitch_output')
first_pitch={'cycles':end['cycles']-start['cycles'],'instructions':end['instructions']-start['instructions'],'fetch_stall_cycles':end['memory_counts']['instruction_fill_stall_cycles']-start['memory_counts']['instruction_fill_stall_cycles'],'entry_ms':start['ms'],'output_ms':end['ms']}
assert next(x for x in rows if x['case']=='prefix-fixed')['pitch_sequence']==next(x for x in rows if x['case']=='prefix-stock')['pitch_sequence']
assert next(x for x in rows if x['case']=='prefix-full')['pitch_sequence']==next(x for x in rows if x['case']=='prefix-pitch-only')['pitch_sequence']
late=[x for x in t['DMA_captures'] if x['ms']>=20 and x.get('completion_margin_cycles',0)<0]
old=json.loads((O/'Digitone-fast-pitch-prefix-full.json').read_text())['runs'][0]
lower_report=json.loads((O/'Digitone-loader-timing-prefix-full-lower-cost.json').read_text());lower=lower_report['runs'][0]
assert lower_report['failure'] is None and lower['halted'] is None and lower['clock']['decode_mismatches']==0
assert all(lower['storage_checks'].values()) and lower['startup_provenance']['snapshot_sha256']==snapshot_hash
assert lower['DMA_summary']['captures_with_unfresh_words']==lower['DMA_summary']['late']==lower['DMA_summary']['unresolved']==0
out={'all_runs_completed':True,'all_cases_meet_sample_freshness':all(row['DMA']['captures_with_unfresh_words']==0 and row['DMA']['late']==0 and row['DMA']['unresolved']==0 for row in rows),'all_cases_meet_FIFO_model':all(row['FIFO_faults']==0 for row in rows),'firmware_modified':False,'snapshot_sha256':snapshot_hash,'assumptions':{'core_hz':264000000,'bus_hz':132000000,'audio_frame_hz':48000,'memory_fill_cycles':40,'memory_writeback_cycles':32,'memory_beat_cycles':8,'contention':True,'cache_occupancy':'new empty PC caches; physical startup cache contents are not restored'},'first_pitch':first_pitch,'first_late_reads':late,'previous_supplied_state_full_margin_us':old['DMA_summary']['minimum_margin_us'],'cases':rows,'limits':['Stock-path, sham and pitch-only controls restore stock instructions for playback from the same mod-initialized startup snapshot; they are not independent stock-loader boots.','Full/fixed runs retain startup-installed helper bytes, hooks and initialized metadata. No reinjection of the helper or header.','Cached-event context still uses the explicit diagnostic commit fixture.','Clock, cache occupancy, memory costs, FIFO occupancy and phase are model assumptions; no physical cache-value simulation or measured device timing.','Long workload is 1.04 seconds with eight keyboard buttons held; button count is not proof of worst-case simultaneous synthesis voices.','Pattern requests do not prove completed pattern replacement.','Finite preservation observations do not prove exclusive RAM ownership.']}
(O/'Digitone-loader-timing-summary.json').write_text(json.dumps(out,indent=2))
out['lower_memory_cost_sensitivity']={'fill_writeback_beat':[20,16,4],'ms':lower['ms'],'DMA':lower['DMA_summary'],'render':lower['render_deadline'],'FIFO_faults':sum(lower['memory_model']['FIFO']['counts'].get(k,0) for k in fault_keys),'storage_checks':lower['storage_checks'],'quantizer_calls':len(lower['quantizer_calls'])}
(O/'Digitone-loader-timing-summary.json').write_text(json.dumps(out,indent=2))
lines=['# Digitone OS 1.42: cycle-aware checks from loader-derived startup','',
 'The timing suite completed from the executed-loader startup snapshot. The previous timing pass is not robust to this starting state: the full mod has a stale sample read under the adverse clock/memory assumptions. Functional table reads and code/storage preservation pass; physical hardware behavior remains unverified.','',
 '## Principal result','',
 '| Case | Duration (ms) | Captures with stale words | Late final-word stores | Minimum margin (µs) | Render-handler period overruns | FIFO faults |','|---|---:|---:|---:|---:|---:|---:|']
for row in rows:
 d=row['DMA'];lines.append(f'| {row["case"]} | {row["ms"]:.3f} | {d["captures_with_unfresh_words"]} | {d["late"]} | {d["minimum_margin_us"]:.3f} | {row["render"]["late"]} | {row["FIFO_faults"]} |')
lines+=['','The fixed-pitch control executes the full helper and restores stock output pitch. Its short pitch sequence matches the stock-path control; the full mod sequence matches the pitch-only control. Memory/compute/fetch-neutral cases deliberately remove costs and are diagnostic counterfactuals, not viable firmware solutions. Handler period overruns are distinct from stale sample data and FIFO faults.','',
 f'The first late full-mod read is at {late[0]["ms"]:.6f} ms: two stale stereo words at {late[0]["start"]}. Its final store arrives {abs(late[0]["completion_margin_cycles"])} modeled core cycles ({abs(late[0]["completion_margin_us"]):.3f} µs) after the capture observer. First native pitch-helper execution takes {first_pitch["cycles"]} modeled cycles and {first_pitch["instructions"]} instructions. The widened trace window reproduces the untraced full run exactly.','',
 '## Continuity and functional checks','',
 'All cases restore the same loader-derived settled-UI snapshot, checked by its hash. The full and fixed-pitch cases retain the startup-installed hooks, 2,324 helper/table bytes and initialized metadata. The same extended flash contents are supplied for application asset reads. Stock-path controls remove selected hooks only in PC memory; sham adds a diagnostic detour.','',
 'Every observed quantizer result matches the pitch oracle, and every quantizer call has a native lookup read from the copied table. Helper bytes and guards remain intact, unexpected reserved-storage writes are absent, timing decoder mismatches are zero, and the final core/timer gap is zero. The original SysEx hash is unchanged.','',
 '## Interpretation and limits','',
 'The short full and fixed-pitch results show that the changed pitch is not required for the failure in this workload. The clean stock-path and sham controls implicate added helper/context execution or its scheduling/cache effects. Neutral-cost cases further constrain that explanation; no physical timing conclusion follows from them.','',
 'These runs assume a 264 MHz core, 132 MHz bus, 48 kHz audio frames and cache-fill/writeback/DMA-beat costs of 40/32/8 cycles. The timing model starts with empty caches rather than the physical cache contents produced by startup. A failing sensitivity model is a reason to improve the margin and model evidence, not proof that the physical Digitone would fail.','',
 f'The short full-mod sensitivity run with lower fill/writeback/beat costs of 20/16/4 cycles has no stale reads, no handler period overruns and {lower["DMA_summary"]["minimum_margin_us"]:.3f} µs minimum observed margin. Neither cost set is a hardware measurement; this result establishes sensitivity to the assumptions.','',
 'The cache-occupancy model uses four ways, 128 sets and 16-byte lines for each 8 KB cache, following the explicit organization in §6.2 of the [NXP MCF5441x Reference Manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf). Its replacement, cost and state approximations remain PC modeling assumptions.','',*['- '+x for x in out['limits']], '',
 'Next: isolate and reduce the added context/pitch execution costs using the measured failing interval, then rerun stock-path/full/fixed controls from this same loader-derived state. Firmware remains unchanged and no flashable image was produced.']
(O/'Digitone-loader-timing-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'sample_freshness_pass':out['all_cases_meet_sample_freshness'],'FIFO_pass':out['all_cases_meet_FIFO_model'],'first_pitch':first_pitch,'cases':[{'case':x['case'],'stale':x['DMA']['captures_with_unfresh_words'],'margin':x['DMA']['minimum_margin_us']} for x in rows]},indent=2))
