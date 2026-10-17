# Digitone OS 1.42 — cache maintenance and shared DDR/DMA timing

The extended PC model completed the matched stock and full-hook comparison with **zero modeled render overruns and zero late or stale audio-buffer reads** under the selected cost scenario. Full hooks had a slowest render of **608.856 microseconds**, leaving **57.812 microseconds** against the 666.668-microsecond budget. Stock's slowest render was **587.060 microseconds**, leaving **79.608 microseconds**.

Firmware files remain unchanged. This test uses ephemeral RAM overlays and diagnostic context fixtures, with no hardware access or flashable firmware generation.

## What changed in the PC model

The isolated model now tracks separate four-way instruction/data caches, 16-byte lines, round-robin replacement, dirty data lines, copyback evictions and the observed cacheable DDR region. CPU cache fills, writebacks and uncached DDR accesses incur configured costs that reduce the execution budget and advance the cycle clock used by the timers.

It recognizes executed MOVEC control writes, global invalidation requests and CPUSHL operations, including physical-address search versus set/way selection, push versus invalidate-only, invalidate-disable flags, and half-cache locking. Register writes update the model's region policies; self-clearing invalidation request bits are cleared locally. These operations follow the [NXP MCF5441x cache chapter](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=180). This is occupancy/timing state, not a cached-byte-value implementation.

Software-started eDMA uses the emulator's Python descriptor walker so the observer can see the actual source/destination ranges, iteration counts, modulo wrapping and descriptor chains. DDR endpoints reserve a shared serialized resource. CPU requests wait behind outstanding DMA reservations. DMA completion status remains unavailable until its reservation completes, and a previous DONE flag is masked while the transfer is active. The firmware's own polling loops execute during that wait.

SSI audio DMA is serviced frame by frame rather than as half-buffer bulk captures. This improves the buffer-freshness observation granularity. SRAM-only SSI traffic is not charged to the DDR resource; shared-crossbar contention for that separate path remains outside this model.

The first diagnostic pilot preceded two corrections: previous-DONE masking and cache-hook registration before first block translation. Its result file is explicitly marked superseded. The long comparison was run after both corrections.

## Independent checks

Thirteen cache/state/serialization checks passed, covering dirty eviction, physical push/invalidation, set/way selection, alias observations, global invalidation and propagation of stalls into the execution budget.

Two native machine-code fixtures also passed:

- A CPU dirty store, CPUSHL DC and MOVEC invalidations produce the expected cache transitions and writeback charge. Pre-registration observes the first CPUSHL execution.
- An SSRT start with a previous DONE bit runs actual firmware-style polling. There were 61 deferred completion polls; the engine completed at cycle 185, after the modeled transfer-ready cycle 171. DONE was set and ACTIVE clear afterward, with the copied payload matching its source.

## Matched longer runs

Both runs start from the same settled stock snapshot, select pattern 2, request **1,000 milliseconds of playback**, and then stop. This is ten times the preceding 100-millisecond active-playback interval. Including selection, warmup and stop, each covers approximately 1.180 seconds of emulated time. The pair took approximately 636 seconds of wall time.

The main-core clock is still an explicit **250 MHz assumption**. Selected costs are **20 extra cycles per instruction/data line fill**, **16 per dirty-line writeback**, and **4 per four-byte DDR DMA/uncached transfer**. They are sensitivity inputs, not measured hardware latencies. The resource serializes requests without reproducing hardware master priorities, burst arbitration or refresh. Floating-point and bitmap shortcuts remain disabled, and both variants use the same Python DMA backend and frame-level SSI observations.

| Measurement | Stock | Full hooks with valid-context fixture |
|---|---:|---:|
| Completed render windows | 1,769 | 1,769 |
| Worst render cycles | 146,765 | 152,214 |
| Worst render duration | 587.060 us | 608.856 us |
| Remaining render margin | 79.608 us | 57.812 us |
| Render overruns | 0 | 0 |
| Post-warmup frame captures | 55,694 | 55,696 |
| Late/unresolved/stale captures | 0 | 0 |
| Minimum final-word store lead | 150.536 us | 129.540 us |
| Deferred software-DMA completion polls | 591 | 572 |

The difference between the two worst observed renders is 21.796 microseconds; this is not an isolated per-hook instruction-cost measurement. Actual emulated durations differ by about 41 microseconds because execution steps finish at block boundaries, accounting for the two-capture difference.

Both variants recorded zero decoder mismatches, no illegal/FPU/line-F decode flags, no engine halt, and no uncovered first execution of a control instruction. The cycle-clock/timer-clock cumulative difference reached approximately 167 microseconds over each run; interrupt entry bookkeeping contributes to that engine limitation. Local store/read leads use the same cycle clock, but these results are not a physical timing certificate.

## Memory and maintenance observations

Both variants transferred the same payload totals on the observed software-DMA channels:

| Channel | Payload bytes |
|---|---:|
| 47 | 3,455,040 |
| 30 | 6,088,800 |
| 42 | 4,755,072 |

Stock recorded 249,993 data fills and 121,639 dirty evictions; full hooks recorded 250,745 and 121,905. The serialized DMA DDR requests reserved 10,843,872 modeled cycles in each run. Aggregate CPU waiting behind other resource requests was 10,810,252 cycles in each run.

Neither playback trace executed a cache-maintenance instruction or changed its cache-control registers. Cache-maintenance behavior is therefore exercised by the separate native fixtures, not demonstrated as a playback event. No modeled dirty cached line overlapped a DMA read, and no modeled resident cached line overlapped a DMA write. Initial cache state is a cold model fixture rather than a physical snapshot, so absence of those observations does not establish complete device coherence.

## Arp output exercised

Five native quantizer calls used the valid retained context. All five observed pitch outputs matched the scale oracle: **57 to 56, 69 to 68, 81 to 80, 57 to 56, and 69 to 68**. Other observed tracks retained their stock pitches. The valid context uses one explicit candidate-metadata injection for the unimplemented cached-replay producer/copy route; this test does not close that capture gap.

Audio hashes differ between stock and the pitch-changing full-hook run. They are retained as artifacts, not used as proof that every audio difference is explained. The stronger timing observation is that every post-warmup captured buffer word was fresh in both runs.

## Limits and next useful work

The model copies DMA payload bytes immediately at launch, while delaying completion status and reserving DDR time. It does not defer individual payload reads/writes to their bus timestamps. Consequently it cannot establish correctness for CPU/DMA accesses that overlap during a transfer, or reproduce real stale-cache byte contents. Coherence overlap counts are diagnostic observations only.

Other limits remain: physical core/reference clock, DDR row/refresh/PHY timing, non-blocking fill overlap, store-buffer timing, hardware arbitration, SRAM-crossbar contention and external voice-processor timing. A one-second playback workload covers more events than the earlier runs but is not sustained-device stress testing. The earlier 40-cycle instruction-fill sensitivity showed a deadline miss; this successful 20-cycle-plus-contention scenario does not invalidate that result.

The next focused PC improvement is timestamped DMA payload visibility, followed by matched higher-latency runs with pattern changes and denser arp traffic. The actual-clock evidence and cached-replay context capture/copy remain separate open issues. Firmware flashing is not an outcome of this audit.

## Saved evidence

- `Digitone-shared-memory-long-summary.json`: compact results and pitch validation.
- `Digitone-shared-memory-long-comparison.json`: complete timing/frame/context trace.
- `Digitone-shared-memory-model-checks.json`: thirteen state/serialization checks.
- `Digitone-cache-maintenance-native-check.json`: machine-code maintenance fixture.
- `Digitone-DMA-completion-native-check.json`: machine-code DMA wait fixture.

Original SysEx SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.
Decoded MAIN OS SHA-256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.
