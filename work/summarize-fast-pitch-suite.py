import pathlib,json,hashlib
O=pathlib.Path('outputs');names=['prefix-stock','prefix-sham','prefix-pitch-only','prefix-fixed','prefix-full','prefix-context-only','prefix-memory-neutral','prefix-compute-neutral','prefix-fetch-neutral','long-stock','long-fixed','long-full']
cases={};rows=[]
for name in names:
 r=json.loads((O/f'Digitone-fast-pitch-{name}.json').read_text());q=r['runs'][0];cases[name]=q
 assert r['failure'] is None and q['halted'] is None and q['clock']['decode_mismatches']==0
 assert r['firmware_before']==r['firmware_after']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
 assert q['DMA_summary']['final_clock_timer_gap_cycles']==0
 for call in q['quantizer_calls']:
  output=next(x for x in q['diagnostic_pitch_controls'] if x['cycles']>=call['cycles'])
  assert output['computed_fixed']==call['expected']<<16,(name,call,output)
 rows.append({'case':name,'ms':q['ms'],'DMA':q['DMA_summary'],'render':q['render_deadline'],'FIFO':q['memory_model']['FIFO'],'pitch_sequence':[(x['track'],x['delivered_fixed']//65536) for x in q['diagnostic_pitch_controls']],'quantizer_calls':q['quantizer_calls']})
old=json.loads((O/'Digitone-first-stale-full.json').read_text())['runs'][0]
def cost(q):
 a=next(x for x in q['checkpoints'] if x['label']=='pitch_entry');b=next(x for x in q['checkpoints'] if x['label']=='pitch_output')
 blocks=[x for x in q['block_costs'] if a['cycles']<=x['cycles']<b['cycles']]
 return {'cycles':b['cycles']-a['cycles'],'instructions':b['instructions']-a['instructions'],'fetch_cycles':b['memory_counts']['instruction_fill_stall_cycles']-a['memory_counts']['instruction_fill_stall_cycles'],'stock_membership_calls':sum(x['pc']=='0x40106b6c' for x in blocks),'unique_instruction_block_bytes':sum({x['pc']:x['size'] for x in blocks}.values())}
costs={'original':cost(old),'optimized':cost(cases['prefix-full'])}
assert costs['optimized']['stock_membership_calls']==0
old_accept=next(x['cycles'] for x in old['checkpoints'] if x['label']=='acceptance')
new_accept=next(x['cycles'] for x in cases['prefix-full']['checkpoints'] if x['label']=='acceptance')
assert old_accept==new_accept==16551004
target=min((x for x in cases['prefix-full']['DMA_captures'] if x['start']=='0x80001b00'),key=lambda x:abs(x['cycles']-16722874))
by={x['case']:x for x in rows}
assert by['prefix-fixed']['pitch_sequence']==by['prefix-stock']['pitch_sequence']
assert by['prefix-full']['pitch_sequence']==by['prefix-pitch-only']['pitch_sequence']
fault_keys=['TX_underflow','TX_overflow','RX_overflow','RX_empty_read','invalid_shift_words_completed']
for r in rows:r['FIFO_faults']=sum(r['FIFO']['counts'].get(k,0) for k in fault_keys)
equivalence=json.loads((O/'Digitone-fast-pitch-equivalence.json').read_text())
assert equivalence['comparisons']==128*128*36
abi=json.loads((O/'Digitone-fast-pitch-hook-ABI.json').read_text())
assert abi['failure'] is None and abi['code_intact'] and len(abi['cases'])==4
for case in abi['cases']:
 assert case['other_registers_and_SR_match_stock'] and case['producer_registers_SR_and_event_match_stock'] and case['invalid_context_falls_back']
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
assert hashlib.sha256(syx.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
summary={'firmware_modified':False,'equivalence':equivalence,'hook_ABI':abi,'first_pitch_costs':costs,'unchanged_first_acceptance_cycle':new_accept,'previously_failing_read_after_optimization':target,'cases':rows,'limitations':['264/132 MHz and memory fill/writeback/beat 40/32/8 are assumed, not hardware measurements.','Native instructions execute, but DMA/cache timing and device state are PC models.','Cached-event context remains an explicit commit fixture; natural capture/copy ownership remains unproven.','The new table is supplied in the RAM overlay and checked intact; its startup installation has not been tested here.','Finite playback coverage does not certify reserved RAM ownership, physical cache coherence, or all voice combinations.']}
(O/'Digitone-fast-pitch-summary.json').write_text(json.dumps(summary,indent=2))
lines=['# Digitone OS 1.42: pitch lookup optimization','',
 'The optimization removes the previously observed stale sample read in the tested PC workload. All nine short controls and all three 1.04-second playback runs complete with zero stale sample reads and zero FIFO faults. The optimized minimum margin is 2.837 µs under the adverse timing assumptions, so the result remains narrow and does not establish hardware readiness.','',
 'The PC helper now uses a nearest-note lookup instead of calling the stock scale-membership routine repeatedly. Its executable body is 178 bytes versus 184; it adds a 420-byte read-only table. The RAM overlay grows from 1,892 to 2,324 bytes and still ends below the existing private pointer at 0x47be1000. Hook entry addresses, context ownership checks, and the other helper bodies remain unchanged. Firmware files are unchanged.','',
 '## Functional checks','',
 '589,824 native-engine comparisons cover all 128 MIDI notes, all 128 roots, and all 36 supported raw scale settings including chromatic. Every result matches the independent nearest-note oracle, including lower-note ties and range edges. Saved D2–D7/A2–A3 registers remain intact. Twenty-five invalid-context or out-of-range fallback cases also pass. Complete hook fixtures on all four tracks preserve event bytes, every other stock register, flags, and the invalid-context fallback.','',
 '## Timing controls','',
 'Short controls repeat the exact 80 ms pattern-2/PLAY prefix from the cause-isolation test. The main optimized cases keep normal memory and computation charges; the neutral cases are separate diagnostic counterfactuals. Every recorded quantizer output matches its independent expected pitch. Native timing decoder mismatches and final core/timer gaps are zero in every case.','',
 '| Case | Emulated duration (ms) | Stale sample reads | Minimum observed write margin (µs) | Handler period overruns | FIFO faults |','|---|---:|---:|---:|---:|---:|']
for r in rows:lines.append(f'| {r["case"]} | {r["ms"]:.3f} | {r["DMA"]["captures_with_unfresh_words"]} | {r["DMA"]["minimum_margin_us"]:.3f} | {r["render"]["late"]} | {r["FIFO_faults"]} |')
lines+=['','Handler period overruns measure total ISR occupancy; they are separate from sample freshness and FIFO faults. Each longer run repeats the pattern-2 workload with eight keyboard buttons held, 800 ms of held playback, release, and STOP. Button count does not prove a simultaneous eight-voice synthesis worst case.','',
 '| First pitch entry to output | Original | Optimized |','|---|---:|---:|']
for label,key in [('Modeled cycles','cycles'),('Instructions','instructions'),('Instruction-fetch cycles','fetch_cycles'),('Stock scale-membership calls','stock_membership_calls'),('Unique executed block bytes','unique_instruction_block_bytes')]:lines.append(f'| {label} | {costs["original"][key]} | {costs["optimized"][key]} |')
lines+=['','The unique-block byte metric counts each executed basic block once inside the measured first pitch interval; it does not count the lookup data or imply a smaller total installation. The fixed-pitch control executes the full optimized helper and then restores the outgoing stock pitch. The pitch-only control changes the pitch without installing the hooks.','',
 f'The first note acceptance stays at core cycle {new_accept:,}, matching the original full-hook run. At the previously failing stereo read, the final-word store is now at cycle {target["last_word_store_cycles"]:,} and the capture observer at {target["cycles"]:,}: {target["completion_margin_us"]:.3f} µs of positive margin, compared with the original 0.587 µs lateness. This improvement uses the charged memory/cache model, without neutralizing costs.','',
 'The lookup index is bounded to 0–419 after the original context checks. Root-relative pitch normalization takes at most eleven ±12 iterations for valid MIDI inputs; there is one lookup and no repeated membership search.','',
 '## Limits','',*['- '+x for x in summary['limitations']], '',
 'Next: connect the new table to the existing PC bootstrap copier and verify startup preservation and cache handoff, then extend playback duration and memory-cost sensitivity. No flashable firmware has been produced.']
(O/'Digitone-fast-pitch-audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'costs':costs,'runs':[{k:r[k] for k in ['case','ms']}|{'stale':r['DMA']['captures_with_unfresh_words'],'margin':r['DMA']['minimum_margin_us'],'FIFO':r['FIFO']['counts']} for r in rows]},indent=2))
