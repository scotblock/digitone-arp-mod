# Digitone OS 1.42: pitch lookup optimization

The optimization removes the previously observed stale sample read in the tested PC workload. All nine short controls and all three 1.04-second playback runs complete with zero stale sample reads and zero FIFO faults. The optimized minimum margin is 2.837 µs under the adverse timing assumptions, so the result remains narrow and does not establish hardware readiness.

The PC helper now uses a nearest-note lookup instead of calling the stock scale-membership routine repeatedly. Its executable body is 178 bytes versus 184; it adds a 420-byte read-only table. The RAM overlay grows from 1,892 to 2,324 bytes and still ends below the existing private pointer at 0x47be1000. Hook entry addresses, context ownership checks, and the other helper bodies remain unchanged. Firmware files are unchanged.

## Functional checks

589,824 native-engine comparisons cover all 128 MIDI notes, all 128 roots, and all 36 supported raw scale settings including chromatic. Every result matches the independent nearest-note oracle, including lower-note ties and range edges. Saved D2–D7/A2–A3 registers remain intact. Twenty-five invalid-context or out-of-range fallback cases also pass. Complete hook fixtures on all four tracks preserve event bytes, every other stock register, flags, and the invalid-context fallback.

## Timing controls

Short controls repeat the exact 80 ms pattern-2/PLAY prefix from the cause-isolation test. The main optimized cases keep normal memory and computation charges; the neutral cases are separate diagnostic counterfactuals. Every recorded quantizer output matches its independent expected pitch. Native timing decoder mismatches and final core/timer gaps are zero in every case.

| Case | Emulated duration (ms) | Stale sample reads | Minimum observed write margin (µs) | Handler period overruns | FIFO faults |
|---|---:|---:|---:|---:|---:|
| prefix-stock | 80.021 | 0 | 32.837 | 1 | 0 |
| prefix-sham | 80.021 | 0 | 32.458 | 1 | 0 |
| prefix-pitch-only | 80.021 | 0 | 32.837 | 1 | 0 |
| prefix-fixed | 80.019 | 0 | 2.837 | 1 | 0 |
| prefix-full | 80.019 | 0 | 2.837 | 1 | 0 |
| prefix-context-only | 80.019 | 0 | 11.545 | 1 | 0 |
| prefix-memory-neutral | 80.011 | 0 | 28.008 | 1 | 0 |
| prefix-compute-neutral | 80.011 | 0 | 24.216 | 1 | 0 |
| prefix-fetch-neutral | 80.019 | 0 | 10.178 | 1 | 0 |
| long-stock | 1040.112 | 0 | 32.837 | 8 | 0 |
| long-fixed | 1040.094 | 0 | 2.837 | 10 | 0 |
| long-full | 1040.073 | 0 | 2.837 | 10 | 0 |

Handler period overruns measure total ISR occupancy; they are separate from sample freshness and FIFO faults. Each longer run repeats the pattern-2 workload with eight keyboard buttons held, 800 ms of held playback, release, and STOP. Button count does not prove a simultaneous eight-voice synthesis worst case.

| First pitch entry to output | Original | Optimized |
|---|---:|---:|
| Modeled cycles | 2758 | 2164 |
| Instructions | 370 | 232 |
| Instruction-fetch cycles | 1960 | 1600 |
| Stock scale-membership calls | 3 | 0 |
| Unique executed block bytes | 924 | 810 |

The unique-block byte metric counts each executed basic block once inside the measured first pitch interval; it does not count the lookup data or imply a smaller total installation. The fixed-pitch control executes the full optimized helper and then restores the outgoing stock pitch. The pitch-only control changes the pitch without installing the hooks.

The first note acceptance stays at core cycle 16,551,004, matching the original full-hook run. At the previously failing stereo read, the final-word store is now at cycle 16,722,145 and the capture observer at 16,722,894: 2.837 µs of positive margin, compared with the original 0.587 µs lateness. This improvement uses the charged memory/cache model, without neutralizing costs.

The lookup index is bounded to 0–419 after the original context checks. Root-relative pitch normalization takes at most eleven ±12 iterations for valid MIDI inputs; there is one lookup and no repeated membership search.

## Limits

- 264/132 MHz and memory fill/writeback/beat 40/32/8 are assumed, not hardware measurements.
- Native instructions execute, but DMA/cache timing and device state are PC models.
- Cached-event context remains an explicit commit fixture; natural capture/copy ownership remains unproven.
- The new table is supplied in the RAM overlay and checked intact; its startup installation has not been tested here.
- Finite playback coverage does not certify reserved RAM ownership, physical cache coherence, or all voice combinations.

Next: connect the new table to the existing PC bootstrap copier and verify startup preservation and cache handoff, then extend playback duration and memory-cost sensitivity. No flashable firmware has been produced.
