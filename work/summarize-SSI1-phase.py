import json,pathlib,hashlib
r=json.loads(pathlib.Path('outputs/Digitone-SSI1-phase-workloads.json').read_text())
rows=[]
for x in r['runs']:
 if 'memory_model' not in x:continue
 f=x['memory_model']['FIFO'];d=x['DMA_summary'];p=x['memory_model']['serial_phase'];hz=x['fsys_assumption_hz']
 assert d['final_clock_timer_gap_cycles']==0
 assert x['clock']['decode_mismatches']==0
 assert f['minimum_TX']>=13 and f['maximum_RX']<=2
 assert not x['SSI_runtime_writes']
 assert p['status_reads']==0 and p['status_writes']==0
 assert x['memory_model']['shared_arbiter']['counts'].get('audio_requests_dropped_while_pending',0)==0
 assert not any(f['counts'].get(k,0) for k in ('TX_underflow','TX_overflow','RX_empty_read','RX_overflow','invalid_shift_words_completed'))
 assert p['error_flags']=='0x0'
 assert not d['late'] and not d['captures_with_unfresh_words']
 rows.append(dict(core_hz=hz,mode=x['mode'],ms=x['ms'],render=x['render_deadline'],FIFO=f,phase=p,DMA=d,pitch=[(a['track'],a['fixed_note']>>16) for a in x['pitch']],oracle=x['quantizer_calls'],workload=x['workload'],SSI_runtime_writes=x['SSI_runtime_writes']))
assert r['failure'] is None,r['failure']
if len(rows)!=4:raise RuntimeError(f'Comparison still running ({len(rows)}/4 complete)')
for hz in (250000000,264000000):
 stock,mod=[x for x in rows if x['core_hz']==hz]
 assert [n for tr,n in mod['pitch'] if tr==2]==[q['expected'] for q in mod['oracle']]
 assert [(tr,n) for tr,n in stock['pitch'] if tr!=2]==[(tr,n) for tr,n in mod['pitch'] if tr!=2]
assert r['firmware_before']==r['firmware_after']=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda'
assert hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
native=json.loads(pathlib.Path('outputs/Digitone-SSI1-final-native-phase-check.json').read_text())
assert native['failure'] is None
for x in native['runs']:
 assert x['DMA_summary']['final_clock_timer_gap_cycles']==0
 assert x['input_clock_checks']==[0,0,0,0]
 assert x['memory_model']['audio_event_timing']['counts'].get('next_frame_deadline_misses',0)==0
 assert not any(x['memory_model']['FIFO']['counts'].get(k,0) for k in ('TX_underflow','RX_overflow','TX_overflow','RX_empty_read','invalid_shift_words_completed'))
s=dict(loaded_phase_code_sha256=pathlib.Path('work/phase-audio-loaded-sha256.txt').read_text(),final_revision_native_check=native,firmware_modified=False,clock_chain=json.loads(pathlib.Path('outputs/Digitone-SSI1-clock-chain.json').read_text()),native_clock_checks=6,phase_checks=67,runs=rows,firmware_sha256=r['firmware_after'],scope='Supplied snapshot branch and phase; short workload includes queued pattern requests, not proof of completed pattern handoff',code_sha256={p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in ('work/phase_audio_dma.py','work/compare-SSI1-phase-workloads.py')})
pathlib.Path('outputs/Digitone-SSI1-clock-phase-summary.json').write_text(json.dumps(s,indent=2))
text='''Each stock/overlay pair ran the same sequence at 250/125 MHz and 264/132 MHz core/bus candidates, with 48 kHz SSI1 audio. The workload selects pattern 2 before playback, holds panel trig buttons 1 and 5, releases them separately, requests pattern 3 and pattern 2 during playback, then stops. Each run lasts about 285 ms, including selection and stop; this is broader input coverage rather than prolonged stress testing. The brief pattern requests are queued-operation coverage, not proof of completed pattern replacement.\n\n| Core candidate | Variant | Completed renders | Worst render (us) | Nominal margin (us) | FIFO faults | Stale output captures |\n|---|---|---:|---:|---:|---:|---:|\n'''
for x in rows:
 hz=x['core_hz'];d=x['render'];worst=d['worst_cycles']*1e6/hz;margin=(d['period_cycles']-d['worst_cycles'])*1e6/hz
 text+=f"| {hz/1e6:g} MHz | {x['mode']} | {d['runs']} | {worst:.3f} | {margin:.3f} | 0 | 0 |\n"
text+='''\nAll four runs ended with zero core/timer discrepancy and zero decoder mismatches. There were no invalid completed shifted words, modeled SSI error flags, late/unresolved output captures or dropped FIFO level requests. TX occupancy stayed at or above 13 words and RX at or below two. The extra panel presses produced note events on tracks 0 and 1. Both core candidates produced the expected target-track changes 57 to 56 and 69 to 68; the four other observed note outputs matched stock.\n\nNo guest SSI1 configuration/status writes or ISR/FCSR reads occurred in these playback intervals. Therefore the native fixtures, rather than these playback runs, exercise MMIO status read and acknowledgement behavior. No claim is made that the hardware deasserts requests on exactly the modeled edge, or that every possible clock writer was excluded.\n\nA separate short native stock/overlay check exercises the final diagnostic-counter correction: both runs have zero frame-window proxy misses, FIFO faults, stale output reads and final core/timer discrepancy. This reporting correction does not change DMA event scheduling. The loaded and final phase-code hashes are preserved in the summary.\n\nThe raw runner was corrected after loading to place descriptive clock-source metadata outside the overlay-only branch. It has no scheduling effect; both stock runs retain their per-run core frequency and CCM snapshot evidence. The saved raw comparison reflects the loaded revision; the final runner hash reflects this metadata-only correction.\n\nEvidence: `Digitone-SSI1-clock-chain.json`, `Digitone-SSI1-clock-main-trace.json`, `Digitone-SSI1-alternate-board-clock-trace.json`, `Digitone-SSI1-clock-aligned-disassembly.txt`, `Digitone-SSI1-native-source-divider-checks.json`, `Digitone-SSI1-serial-phase-checks.json`, `Digitone-SSI1-phase-workloads.json`, `Digitone-SSI1-final-native-phase-check.json`, and `Digitone-SSI1-clock-phase-summary.json`. Original SysEx and decoded MAIN hashes remain unchanged.\n'''
p=pathlib.Path('work/SSI1-phase-report-draft.md').read_text().replace('Pending results from the stock and full-overlay workload at both clock candidates.',text)
pathlib.Path('outputs/Digitone-OS1.42-SSI1-clock-phase-audit.md').write_text(p)
print(json.dumps([dict(hz=x['core_hz'],mode=x['mode'],worst_us=x['render']['worst_cycles']*1e6/x['core_hz'],runs=x['render']['runs']) for x in rows]))
