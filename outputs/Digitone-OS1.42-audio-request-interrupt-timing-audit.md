# Digitone OS 1.42: audio request and completion-interrupt timing

## Result

Audio requests now enter the shared DMA controller at scheduled core-cycle timestamps. The request phase advances by an exact fractional period, without moving late requests to the next scheduler checkpoint or skipping elapsed requests. Payload and request events are merged chronologically.

Half/major completion interrupts are associated with the final payload-write timestamp. Pending completion interrupts wake the outer execution loop; they no longer need to wait for the next audio frame. CPU and interrupt-controller masks still determine whether a vector can be delivered.

These changes close the outer-frame request/delivery gap in the PC model. They do not make CPU execution instruction-cycle-exact or establish real-device timing.

## Implementation

The isolated module `work/precise_audio_dma.py` extends the existing shared arbiter. The comparison runner uses it through `work/compare-precise-audio-DMA.py`; baseline modules remain available.

- SSI requests use the core clock as their timing authority. At the assumed 250 MHz and 48 kHz request rate, the period is exactly `15625/3` cycles; individual integer deadlines alternate as fractional phase requires.
- RX and TX requests from one frame share their scheduled timestamp and are queued together before arbitration.
- Request arrivals and DMA payload beats are processed in timestamp order, including multiple requests elapsed during a late service boundary.
- A completion flag is asserted only after the final payload beat is processed. Its logical assertion timestamp is distinct from the CPU boundary that observes it.
- Scheduler wakeups cover audio payload progress and eligible pending completion interrupts. Native vector entry occurs outside the running CPU hook, preserving the existing exception/frame path.
- Measurements distinguish logical transfer completion, event-service lateness and completion-to-vector-attempt latency. IRQ entry cost is recorded separately from the attempt timestamp.

## Controlled checks

Fifteen checks passed: no early request, common RX/TX timestamp, no early completion interrupt, final-beat assertion, completion before the following frame, CPU IPL masking, interrupt-controller masking, native emulator vector entry after unmasking, delivery-to-assertion accounting, delayed-service catch-up, fractional phase without drift, exact fractional next-arrival deadline, retained arrival timestamps, deliberately induced deadline misses and explicitly counted overlapping-request drops.

The overloaded fixtures intentionally produce failures in the timing detector to verify that it catches them. Those failures are separate from the successful playback comparisons below.

## Stock/full-hook comparison

Both variants used the same settled stock snapshot, synthetic card and pattern 2, with 100 ms of active playback. Preparation and stopping brought each run to about 280.167 ms. This is a short comparison; the earlier one-second comparison exercised the previous timing model.

The full-hook variant retains the injected candidate root/scale metadata fixture. Natural cached-context capture and copying are not established by this test. Its one observed quantizer output matched the oracle, 57→56. Other observed tracks' pitch events matched stock.

| Measurement | Stock | Full PC hooks |
|---|---:|---:|
| Completed renders | 419 | 419 |
| Worst render, assumed µs | 569.128 | 591.340 |
| Modeled render deadline margin, µs | 97.540 | 75.328 |
| Missed render deadlines | 0 | 0 |
| Stale audio captures | 0 | 0 |
| Emitted frame requests | 13,450 | 13,450 |
| Completed RX/TX minor transfers | 26,898 | 26,898 |
| Dropped emitted requests | 0 | 0 |
| Next-frame completion proxy misses | 0 | 0 |
| Maximum request-to-completion, cycles | 99 | 97 |
| Maximum request service lateness, cycles | 201 | 198 |
| Maximum completion-to-IRQ-attempt, cycles | 341 | 190 |
| Completion IRQ assertions / vector 174 deliveries | 420 / 420 | 420 / 420 |
| Vector 191 entries | 420 | 420 |

At the assumed clock, maximum completion-to-attempt latency is 1.364 µs for stock and 0.760 µs for the full hooks. These are model measurements, not physical interrupt-latency bounds. Interrupt entry incurs additional modeled cost after the attempt.

Each finite run ends with TX channel 54 active and RX channel 52 waiting. The accounting reconciles: 26,900 emitted minor requests = 26,898 completed + two pending/active. No completion IRQ coalescing was observed. Neither run halted or reported decoder mismatches. Only completed render intervals are included in the deadline table; an in-flight final interval is not automatically a failure.

The playback runs preceded a one-cycle correction to fractional next-frame deadline rounding. That correction changes only the deadline check, not request generation, arbitration, payload execution or interrupt delivery. The corrected controlled test passes. Independently, every playback transfer's latency is below 100 cycles, compared with a minimum frame interval of 5,208 cycles, proving the zero-miss result also holds with the corrected deadline.

Changes in render costs relative to the previous model reflect different scheduling. They are not evidence that device firmware became faster.

## Remaining limits and next target

The CPU clock still advances by basic blocks and modeled memory stalls. Events can be serviced after their logical timestamp, and source bytes/flags become observable at those service boundaries. Interrupts enter at the first available outer execution boundary, subject to masking. The observed lateness is explicitly measured; exact instruction-level ordering remains unverified.

The next-frame deadline is a proxy. Codec FIFO depth, watermarks, request handshake, underrun/overrun and physical bus timing are not represented. Unknown external receive audio remains preserved rather than invented. Other peripheral DMA paths, queued descriptor edits and full per-beat register progress retain the shared arbiter's prior limitations.

SSI now follows core cycles, while PIT/session time still uses outer-loop accounting. Their maximum observed gap was 61.844 µs in stock and 61.820 µs with hooks. External exception-entry and flow-resolution costs contribute to this difference. The next focused task is reconciling those clock domains, then using verified SSI FIFO/watermark behavior to replace the next-frame proxy.

Core frequency remains assumed at 250 MHz. Cache fills, dirty writebacks and bus beats remain assumed at 20, 16 and four cycles respectively. Documented DMA reset priority fields are seeded in the PC model; their physical bootstrap inheritance remains unverified.

## Evidence and preservation

- `Digitone-precise-audio-timing-checks.json`: fifteen controlled checks.
- `Digitone-precise-audio-timing-pilot.json`: complete stock/full-hook measurements.
- `Digitone-precise-audio-timing-summary.json`: integrity, request conservation, pitch and corrected-deadline assertions.

No hardware was accessed and no flashable image was produced. The original SysEx and MAIN OS hashes remain:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- MAIN OS: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

Final isolated timing-module SHA-256: `81c3aa4398446de37b7d5a1fabdc5dac457b448922e592aa4175dc79f75226ad`.
