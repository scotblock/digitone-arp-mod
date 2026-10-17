# Digitone OS 1.42 — cycle-aware render and DMA deadlines

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
| Stock | 510 | 413.604 | 253.064 | 0 | 956.856 |
| Stock-instruction detour | 510 | 413.676 | 252.992 | 0 | 955.044 |
| Full hooks, cached-context fallback | 509 | 421.872 | 244.796 | 0 | 948.576 |
| Full hooks, valid-context fixture | 509 | 423.132 | 243.536 | 0 | 947.316 |

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

Original SysEx SHA256 before and after: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`. No modified firmware or flashable container was produced.
