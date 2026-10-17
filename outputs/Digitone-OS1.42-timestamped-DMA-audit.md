# Digitone OS 1.42: timestamped DMA payload audit

## Result

The PC engine no longer copies software-started DMA payloads immediately at launch. Source reads and destination writes are separate scheduled events. Source bytes are fetched when the read event is serviced; destination bytes become visible when the write event is serviced. Scatter/gather descriptors are fetched after the preceding payload, and DONE is published after the final write.

This closes the immediate-copy gap for the exercised software DMA path. It does not establish hardware-equivalent timing or complete eDMA behavior.

## Verification

- Eleven controlled checks passed: unchanged destination at launch, ACTIVE/DONE behavior, early reads, source changes across read events, partial visibility, completion after the last write, dynamic scatter/gather descriptors, modulo wrapping, unequal source/destination beat sizes, and drained fixture queues.
- A native guest-code start-and-poll fixture passed. It made 61 deferred completion polls before observing DONE and the correct payload. Its maximum event-service lateness was six assumed core cycles.
- A native cache-maintenance fixture passed, exercising a dirty store, CPUSHL and MOVEC invalidation. The dirty line's writeback was charged before invalidation.
- Thirteen existing cache/bus state checks passed after the implementation changes.

Controlled tests explicitly advance and service the clock; they test temporal semantics, not cycle-exact CPU execution. The long runs service events at translated CPU block, guest-memory and peripheral boundaries.

## Matched playback comparison

Each variant used the same settled stock snapshot, synthetic card and pattern 2, with one second of active playback. Including preparation and stopping, each run covered approximately 1.180 seconds. The full-hook variant used PC RAM overlays, the native pitch quantizer and one injected candidate root/scale metadata context. This is not a cold-start or complete natural-context capture test.

Timing assumptions: 250 MHz core, 20-cycle cache-line fills, 16-cycle dirty writebacks and four cycles per four-byte DMA/uncached bus beat, with serialized bus contention. These values remain assumptions.

| Measurement | Stock | Full PC hooks |
|---|---:|---:|
| Completed renders | 1,769 | 1,769 |
| Worst render | 579.280 µs | 589.992 µs |
| Margin against modeled render deadline | 87.388 µs | 76.676 µs |
| Missed render deadlines | 0 | 0 |
| Audio-frame captures after warmup | 55,692 | 55,697 |
| Late or stale captured audio frames | 0 | 0 |
| Minimum captured-buffer store lead | 158.724 µs | 147.592 µs |
| Maximum payload-event service lateness | 71 cycles | 71 cycles |
| Active software DMA channels at test end | Channel 30 | None |
| Queued payload events at test end | 1 | 0 |

At the assumed clock, 71 cycles is 0.284 µs. This records the difference between a scheduled event timestamp and the boundary at which the engine serviced it; it is not a bound on real-device timing error. The stock run ends during a transfer. Its queue was not drained, and transfer totals cannot be compared as though both runs ended at identical DMA phases.

Neither run halted or reported decoder mismatches. The five target-track pitch outputs matched the independent expected values: 57→56, 69→68, 81→80, 57→56, 69→68. Other observed tracks' pitch events matched stock. Different audio hashes are not, by themselves, evidence of an unwanted audio change: the target pitches and event timing differ.

The reduced worst render costs relative to the previous immediate-copy model reflect changed emulator scheduling. They do not establish that the hardware or modified firmware would run faster.

## Remaining limitations and next check

The exercised descriptors contain minor-loop self-links: 47→47, 30→30 and 42→42. No cross-channel minor links were observed in this workload. The walker executes their payload iterations, but explicit self-link restart/arbitration behavior is not modeled. The diagnostic counter named `unsupported_minor_link_descriptors` counts those flagged descriptors; it does not mean their payload was omitted.

The hardware manual distinguishes self-link arbitration from continuous reactivation using the eDMA CR.CLM setting. The next focused check is to recover the firmware's actual CLM and channel-priority configuration, then model and test those self-link boundaries. See [NXP MCF54418 reference manual, chapter 19, channel linking](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=406).

Other limits remain: descriptor progress registers update at completed descriptor boundaries; cached byte values are not represented separately from memory; real DDR arbitration, refresh and store buffers are uncalibrated; major linking and interrupt behavior are not fully validated. SSI audio is still a separate frame-level peripheral model. No cache-maintenance instructions were observed during the playback comparison, so the native maintenance fixture supplies the direct evidence for that path.

## Preservation and evidence

No hardware was accessed, no flashable firmware was produced, and the original files remain unchanged:

- Original SysEx SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded MAIN OS SHA-256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

Saved evidence:

- `Digitone-timestamped-DMA-long-summary.json`: summarized comparison and pitch validation.
- `Digitone-timestamped-DMA-long-comparison.json`: complete run measurements and sampled events.
- `Digitone-timestamped-DMA-visibility-checks.json`: eleven controlled visibility checks.
- `Digitone-timestamped-DMA-native-check.json`: native start/poll fixture.
- `Digitone-timestamped-cache-maintenance-native-check.json`: native cache-maintenance fixture.
- `Digitone-shared-memory-model-checks.json`: thirteen cache/bus checks.

PC implementation: `work/timestamped_dma.py`, with the existing shared-memory timing module and comparison runner. Digiemu source baseline: `24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2`.
