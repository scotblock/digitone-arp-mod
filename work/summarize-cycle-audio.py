import pathlib,json,hashlib
out=pathlib.Path('outputs')
def read(n):return json.loads((out/n).read_text())
simple=read('Digitone-cycle-audio-first-comparison.json');pattern=read('Digitone-cycle-audio-pattern2.json');valid=read('Digitone-cycle-audio-valid-context.json')
for report in [simple,pattern,valid]:
 assert report['failure'] is None and report['firmware_before']==report['firmware_after']
 for run in report['runs']:
  assert run['halted'] is None and run['clock']['decode_mismatches']==0
  assert not any(f['flags']&7 for f in run['decoder_flags'])
  assert run['render_deadline']['late']==0 and run['DMA_summary']['late']==0 and run['DMA_summary']['unresolved']==0
  assert run['DMA_summary']['pending_mixer_capture_count']==0
for run in pattern['runs']+valid['runs']:assert run['DMA_summary']['captures_with_unfresh_words']==0
assert len(set(run['audio_sha256'] for run in simple['runs']))==1
assert len(set(run['audio_sha256'] for run in pattern['runs']))==1
actual=valid['runs'][0];q=actual['quantizer_calls'];assert len(q)==2 and all(x['word']=='0x800040bd' for x in q)
assert [(x['note'],x['expected']) for x in q]==[(57,56),(69,68)]
assert [x['fixed_note']>>16 for x in actual['pitch'] if x['track']==2]==[56,68]
fsys=valid['fsys_assumption_hz'];period=round(fsys*32/48000)
table=[]
for run,label in [(pattern['runs'][0],'Stock'),(pattern['runs'][1],'Stock-instruction detour'),(pattern['runs'][2],'Full hooks, cached-context fallback'),(actual,'Full hooks, valid-context fixture')]:
 d=run['render_deadline'];table.append({'variant':label,'completed_renders':d['runs'],'worst_cycles':d['worst_cycles'],'worst_us':d['worst_cycles']*1e6/fsys,'period_us':period*1e6/fsys,'margin_us':(period-d['worst_cycles'])*1e6/fsys,'late_renders':d['late'],'DMA_captures_after_warmup':run['DMA_summary']['after_warmup_captures'],'minimum_buffer_completion_lead_us':run['DMA_summary']['minimum_margin_us'],'unfresh_buffer_captures':run['DMA_summary']['captures_with_unfresh_words']})
summary={'firmware_modified':False,'firmware_sha256':valid['firmware_after'],'model_fsys_assumption_hz':fsys,'table':table,'real_scale_search_executed':True,'cached_context_gap_observed':True,'simple_and_pattern2_fallback_audio_equal_across_variants':True,'instruction_decoder_mismatches':0,'observed_render_misses':0,'observed_DMA_late_or_unfresh_captures':0,'limits':['Short restored-snapshot sessions, not worst-case testing.','250 MHz is an explicit assumption, not a verified device PLL result.','No memory waits, bus contention or measured cache penalties; no dual instruction issue, alignment penalties not charged.','Existing bulk SSI DMA, DSP stepping and interrupt delivery model.','Valid scale search uses an explicit candidate fixture; cached producer capture/copy remains unimplemented.','Physical timing safety and global storage ownership remain unproven.']}
(out/'Digitone-cycle-audio-deadline-summary.json').write_text(json.dumps(summary,indent=2))
rows='\n'.join(f"| {t['variant']} | {t['completed_renders']} | {t['worst_us']:.3f} | {t['margin_us']:.3f} | {t['late_renders']} | {t['minimum_buffer_completion_lead_us']:.3f} |" for t in table)
text=f'''# Digitone OS 1.42 — cycle-aware render and DMA deadlines

The cycle-aware PC model showed no render overruns or late/unfresh DMA buffer captures in these bounded runs. At an explicitly assumed 250 MHz, the full hooks with a valid scale context completed their slowest observed render in 423.132 µs, leaving 243.536 µs within the 666.668 µs period. This is modeled margin, not verified physical-device margin.

Firmware files remain unchanged.

## Measurement setup

The pinned engine's `CycleClock`/`CycleStepper` replaced instruction-count and fixed-block clocks. It uses the engine's instruction timing tables, register/address dependency stalls and conservative branch ranges. The assumed core frequency was 250,000,000 Hz; the OS 1.42 device clock/PLL has not been established here.

Floating-point and bitmap shortcuts were disabled (`hle=False`) so the real firmware routines execute. The same stock settled snapshot, synthetic card and restored device models were used. Helper code/private ready metadata were supplied as PC fixtures; this timing test does not rerun cold startup.

Render duration is main interrupt vector 191 entry through return, including nested interrupt time as recorded by the cycle model. The nominal period is 32 frames at 48 kHz: about 666.667 µs, rounded to 166,667 modeled cycles. Observed median render entry spacing was 166,691 cycles in the pattern-2 comparison. Incomplete boundary renders are not counted as completed renders.

At DMA capture, the observer tracked guest stores to the SRAM output buffer, checked each captured word against the preceding capture of that buffer half, and measured the final-word store's lead relative to the bulk read. The 20 ms warmup was excluded from those capture summaries.

## Arp-bearing pattern results

Each comparison selected pattern 2 before Play, then played and stopped over about 340.4 emulated milliseconds. These are separate reproducible sessions, not one continuous stress run.

| Variant | Completed renders | Worst render, µs | Period margin, µs | Late renders | Minimum buffer store lead, µs |
|---|---:|---:|---:|---:|---:|
{rows}

Each variant had 481 DMA captures after warmup. All were resolved, with zero pending-mixer captures, zero late final-word stores, and zero captures containing words that had not been rewritten since the previous capture of that half. The smallest observed buffer store lead was 947.316 µs.

The buffer-store lead is distinct from the render-period margin: the output pipeline fills alternating buffer halves ahead of their consumption. It must not be read as an additional per-render execution budget.

The full valid-context run's worst render was 9.528 µs longer than the stock run's observed maximum. This is a difference between bounded run maxima, not an isolated cost of a single helper call or a worst-case overhead guarantee. The full-hook run without the candidate fixture had a maximum of 421.872 µs.

No instruction-length decoder mismatch or illegal/FPU/line-F flagged instruction occurred in any measured run. Supervisor instructions and other informational decoder flags still occur normally.

## Cached context gap and actual quantizer work

Selecting pattern 2 while stopped reached a cached replay path. The full native hooks reached the quantizer twice, but the automatically retained word was zero. It therefore used its fallback path. This is consistent with the outstanding cached producer/context-copy coverage gap; entering the quantizer alone is not evidence of a valid captured scale.

To measure the scale-search path, a separate explicit PC fixture supplied candidate word `800040bd` for the validated fixed-pool event immediately before the native retained commit. Stock acceptance, native commit, retained read and quantizer instructions then executed normally. No pitch register was changed by the observer.

The native calls constrained `57 → 56` and `69 → 68`, matching the independent scale oracle, with fixed-point outputs verified. This run supplies the valid-context row above. It does not prove automatic capture for that cached path or implement its missing copy hook.

## Comparison with the previous audio mismatch

A first 240.4 ms cycle-clock comparison on the original pattern produced identical audio hashes for stock, the pure stock-instruction detour and all hooks. The pattern-2 stock/detour/full-fallback runs also produced identical audio hashes. The valid-context fixture intentionally changed pitch and therefore audio.

The previous instruction-based timing experiments could capture a buffer while its right-channel store was pending. No such overlap occurred in the observed cycle-aware runs at this assumed frequency. This supports timing calibration as a cause of the reproduced discrepancy; it does not show that every prior long-session difference has been eliminated. The new sessions are short and use a different time model and disabled arithmetic shortcuts.

## Limits and next step

The model assumes zero-wait memory, no bus contention or measured cache miss penalties. It does not model dual instruction issue, and it does not charge alignment penalties. Interrupt entry is estimated rather than physically measured. The existing bulk DMA capture and batch DSP stepping remain; these are not sample-by-sample hardware bus measurements.

The cycle counter and timer counter have a small accumulated offset: the largest recorded gap in these pattern-2 runs was 12,112 cycles (48.448 µs at the assumed frequency), reflecting accounting/dispatch boundaries. Store-to-capture margins use the same cycle counter on both sides, but this offset limits precision of cross-clock timestamp interpretation. Model results must not be presented as precise device timings.

The cases do not cover eight-voice worst loads, every effect, all root/scales, long sessions, full queued/live context handling, writer races or unmodelled devices. The previous cold-start-through-playback result remains separate evidence; full RAM ownership and physical cache coherence remain unproven.

The next focused step is to establish the firmware's actual core clock/PLL setup and assess cache/memory timing sensitivity before treating the measured margin as relevant to hardware. The cached context producer/copy gap also remains an implementation target. No hardware flash or firmware rebuild is warranted by these measurements alone.

## Evidence

* `Digitone-cycle-audio-first-comparison.json`: original-pattern stock/detour/full comparison.
* `Digitone-cycle-audio-pattern2.json`: pattern-2 comparison with automatic cached fallback.
* `Digitone-cycle-audio-valid-context.json`: explicit candidate fixture and actual scale-search work.
* `Digitone-cycle-audio-deadline-summary.json`: consolidated assertions and numerical results.

Original SysEx SHA256 before and after: `{valid['firmware_after']}`. No modified firmware or flashable container was produced.
'''
(out/'Digitone-OS1.42-cycle-aware-audio-deadline-audit.md').write_text(text,encoding='utf-8')
print('PASS cycle deadline evidence:',summary)
