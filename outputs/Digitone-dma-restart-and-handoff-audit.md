# Digitone: DMA restart and complete cycle-aware handoff

The shared DMA model now retains a single software START request, coalesces overlapping requests with self-links, and updates SADDR/DADDR/CITER after each minor. It samples the descriptor when arbitration grants service. Twelve dedicated boundary/payload checks and twenty existing shared-arbiter checks pass. Firmware remains unchanged.

The former exception occurs in stock channel 47: at cycle 10,565,841, `4009c8c4` reprograms and starts a new transfer while the previous 58-minor transfer is around minor 35 under doubled memory costs. Pending START coalesces with the next self-link; active address/count rewrites lose to minor writeback, while BITER survives. The corrected model exposes the consequence instead of aborting. These rules follow [NXP MCF5441x Reference Manual, chapter 19](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf).

## Sensitivity controls

All cases use inherited loader/startup state, disable acceptance-time metadata injection and run stock routines with HLE disabled. Normal fill/writeback/beat costs are 40/32/8; 1.5× costs are 60/48/12; doubled costs are 80/64/16.

| Case | Duration (ms) | Quantizations | Stale captures | Minimum margin (µs) | Busy requests |
|---|---:|---:|---:|---:|---:|
| stock-normal | 80.031 | 0 | 0 | 30.481 | 0 |
| full-normal | 80.021 | 1 | 0 | 4.375 | 0 |
| stock-double | 80.021 | 0 | 789 | -1133.106 | 1 |
| full-double | 80.021 | 0 | 789 | -1133.106 | 1 |
| stock-150pct | 1040.071 | 0 | 291 | -1274.242 | 0 |
| full-150pct | 1040.071 | 0 | 296 | -1259.936 | 0 |
| stock-double-voices | 1040.125 | 0 | 13459 | -2429.402 | 1 |
| full-double-voices | 1040.125 | 0 | 13459 | -2429.402 | 1 |
| prepared-stock-normal | 90.016 | 0 | 0 | 114.561 | 0 |
| prepared-full-normal | 90.016 | 1 | 0 | 109.936 | 0 |
| prepared-stock-150pct | 90.005 | 0 | 75 | -954.205 | 0 |
| prepared-full-150pct | 90.005 | 0 | 75 | -954.205 | 0 |
| prepared-stock-double | 90.005 | 0 | 975 | -2322.076 | 0 |
| prepared-full-double | 90.005 | 0 | 975 | -2322.076 | 0 |

The original panel-request sensitivity tests did not actually enter pattern 2 at the slower costs. Their zero hook calls do not demonstrate hook safety. The additional `prepared-*` controls begin on the confirmed native pattern-2 state; normal costs execute capture and quantization, while the slower windows still fail audio freshness before observed hook execution.

## Complete handoff

Timed playback completes an actual pattern replacement at cycle 642,039,627 (2431.964 ms). The interval from backing-pointer publication to the recovered completion point is 3,933 modeled cycles (14.898 µs). This measures those two observed points, not every preceding pattern preparation operation.

The delayed source note remains `0x800040bd` and outputs 57 → 56 after replacement. Fresh receiving-pattern notes are independently constructed from backing `407b00cc` and retain `8000433b`. Matches use event address, allocation generation and execution order.

Across 3720.047 ms, the handoff workload records 2 stale captures after 20 ms and a minimum observed completion margin of 14.390 µs. See the summary for FIFO counters and handler-period overruns; these are distinct measurements.

The queued request → completed replacement interval is 2061.952 modeled ms, including the wait for the stock pattern boundary. The matching stock-instruction handoff records 0 stale captures and a minimum margin of 4.833 µs.

## Limits

- Timing assumes a 264 MHz core, 132 MHz bus and 48 kHz audio; memory costs are sensitivities, not calibrated hardware measurements.
- Stopped native pattern preparation executes without cycle costs; timing begins before PLAY and runs uninterrupted through replacement and old-note acceptance.
- Roots/scales, delayed publication timestamp, MIDI/input settings and initial FIFO phase are explicit PC fixtures; event eligibility and retained metadata are stock-produced.
- Hardware cache-value coherence, codec phase and exhaustive RAM ownership remain unverified.
- Active internal SADDR/DADDR/NBYTES readback and register-bus stall cycles are not comprehensively modeled. Request latching and per-minor writeback are the verified scope.

Positive completion margins do not establish freshness: a stale capture can refer to the previous buffer completion. The two modified stale captures coincide with the first fresh receiving-pattern quantization, whose pitch remains 57. This establishes a timing regression in this workload if the stock control has no stale captures; it does not yet isolate its cause. Active descriptor writeback behavior is a modeled interpretation of the register rules, not a hardware measurement.

These PC results do not establish physical timing safety or justify flashing the device.
