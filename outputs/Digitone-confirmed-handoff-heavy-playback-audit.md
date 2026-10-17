# Digitone OS 1.42: confirmed handoff and heavier PC playback

The queued/sustained functional handoff is confirmed in the PC engine. The active modified playback case exposed one stale stereo DMA read under doubled memory costs; its stock counterpart had none. Firmware remains unchanged. These are PC observations and assumed-cost timing tests; they do not establish readiness to flash.

## Confirmed queued and sustained handoff

The native playback writer at 0x40095926 replaced backing 0x407b00cc with 0x407c61e9 at 2589.850 ms. Execution reached the publication-block completion at 0x40095bd6 and subsequently produced/consumed notes from the new backing. This is evidence of replacement, beyond a queued panel request.

Event 0x4199dbfc, allocation generation 6, was published from the old backing at 875.183 ms. It was still pending at replacement and was accepted from the same event generation at 2598.021 ms under the new backing. The queued crossing was deliberately created by delaying one actual stock-produced note by 48,000,000 queue ticks in PC RAM. Stock insertion, transition and consumption code executed.

MIDI CC64 traversed the UART9 receive ring, interrupt, parser and recovered stock controller handler. Track 4 (zero-based 3) had sustain enabled and a non-empty held-note list at replacement. A later CC64=0 cleared both. Input bytes and input-enable settings were explicit PC fixtures; no hardware MIDI ports were opened.

A separate overlay probe captured 0x800000bd from the old pattern and preserved the delayed event generation across replacement. The delayed event was a direct note, and its arp quantizer did not execute. This does not prove arp retained-context pitch behavior during a handoff.

## Longer playback and memory sensitivity

Core/bus candidates: 264/132 MHz; conditional audio rate: 48 kHz. Baseline costs are fill/writeback/beat 20/16/4 cycles; adverse costs are 40/32/8. The serial-phase FIFO and shared DMA arbiter models were used with actual delayed payload copying. Seven allocation bits stayed set during the heavier held-note interval. Render timing measures vector 191 entry through RTE, including preemption and handler cleanup; handler-period overruns and stale payload reads are separate measurements.

| Case | Emulated ms | Handlers | Worst handler µs | Period margin µs | Overruns | Stale reads | Valid quantizer calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| nominal-stock | 1010.08 | 1514 | 525.43 | 141.24 | 0 | 0 | 0 |
| nominal-all | 1010.08 | 1514 | 532.15 | 134.52 | 0 | 0 | 0 |
| adverse-stock | 1010.07 | 1514 | 639.58 | 27.09 | 0 | 0 | 0 |
| adverse-all | 1010.06 | 1514 | 648.38 | 18.29 | 0 | 0 | 0 |
| adverse-pattern2-stock | 1040.11 | 1559 | 714.67 | -48.00 | 8 | 0 | 0 |
| adverse-pattern2-all-active-context | 1040.10 | 1559 | 746.81 | -80.14 | 10 | 1 | 4 |

The four paired baseline/adverse runs exercise the installed hook path but contain no valid arp quantizer calls. They therefore measure heavier playback and inactive-context overhead, not the active scale-lock workload. Supplementary cases are listed separately to avoid merging different workloads.

In the arp-enabled adverse pair, stock had 8 handler-period overruns but no stale reads. The overlay had 10 overruns and one stale 8-byte stereo payload at approximately 63.334 ms: its next final-word store occurred 155 cycles (0.587 µs) after capture. Neither case recorded FIFO underflow/overflow or invalid shifted words, and the final core/timer gap was zero. The modified workload therefore fails this assumed-cost payload-freshness check even though FIFO occupancy stays healthy.

All four native quantizer outputs matched the oracle: 57→56, 69→68, 81→80, and 57→56 on zero-based track 2. The other 13 observed pitches matched stock. The valid context word was explicitly supplied at the commit hook for these timing cases; natural cached-context capture is not proved. This pair combines helper execution and intended pitch changes, so it does not isolate which contribution caused the first late store.

## What remains

- Finite runs from one experimental OS 1.42 snapshot, not hardware validation.
- Seven allocation bits do not establish an eight-voice worst workload or every voice/effect algorithm.
- Clock candidates and memory/cache costs assumed; physical cache values, codec phase and unrelated peripheral DMA remain unverified.
- Timing playback and functional handoff are separate experiments; no cycle-aware full handoff tested.
- Cached producer context-copy implementation and full reserved-RAM ownership remain unresolved.
- Valid-context timing fixtures inject metadata at commit; they do not prove natural cached-context capture.

Next: trace the first stale-read render and use a stock-instruction detour / fixed-pitch control to separate hook, cache, scheduling and changed-pitch costs. Then combine a confirmed arp-producing queue crossing with natural cached-context capture and retained-context pitch output, and measure that full handoff under the cycle-aware model. Physical timing still needs independent evidence.
