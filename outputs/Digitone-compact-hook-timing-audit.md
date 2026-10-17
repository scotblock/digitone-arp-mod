# Digitone OS 1.42: compact hook timing controls

The compact PC-only overlay completed all twelve controls. Sample freshness and FIFO checks pass under the same assumed clock and memory costs. The original firmware remains unchanged; no installable firmware was generated.

## Change and native validation

The resolver saves its scratch register once across the four header comparisons. The pitch helper removes two scratch-register saves whose values are overwritten before use. Internal branches use shorter encodings where they fit. All entry addresses, validation checks, table bytes and startup/copy layout are retained. Unused bytes are unreachable padding, so the whole copied overlay remains 2,324 bytes.

| Helper | Previous body bytes | Compact body bytes |
|---|---:|---:|
| resolve | 166 | 112 |
| read | 74 | 62 |
| pitch | 292 | 238 |

Native differential tests cover 72 resolver/read cases and 72 pitch cases across four tracks, including invalid context and event/cache predicates. All compared registers, materialized condition flags and event/record contents match the prior code. The actual displaced stock hook instructions also pass the four-track ABI checks, plus 162 sampled quantizer checks. The quantizer itself was unchanged.

The compact code passed a fresh actual loader-to-application run, initialization and playback. Timing runs use that new loader-derived settled snapshot and the matching ephemeral flash contents. Full/fixed cases retain installed hooks and metadata rather than reinjecting them.

## Timing results

| Control | Duration ms | Stale captures | Previous stale captures | Minimum margin µs | Render period overruns | FIFO faults |
|---|---:|---:|---:|---:|---:|---:|
| prefix-stock | 80.031 | 0 | 0 | 30.481 | 1 | 0 |
| prefix-sham | 80.031 | 0 | 0 | 30.216 | 1 | 0 |
| prefix-pitch-only | 80.031 | 0 | 0 | 30.481 | 1 | 0 |
| prefix-fixed | 80.021 | 0 | 1 | 2.807 | 1 | 0 |
| prefix-full | 80.021 | 0 | 1 | 2.807 | 1 | 0 |
| prefix-context-only | 80.021 | 0 | 0 | 11.288 | 1 | 0 |
| prefix-memory-neutral | 80.021 | 0 | 0 | 15.511 | 1 | 0 |
| prefix-compute-neutral | 80.011 | 0 | 0 | 8.542 | 1 | 0 |
| prefix-fetch-neutral | 80.021 | 0 | 0 | 7.920 | 1 | 0 |
| long-stock | 1040.105 | 0 | 0 | 30.481 | 8 | 0 |
| long-fixed | 1040.115 | 0 | 1 | 2.807 | 11 | 0 |
| long-full | 1040.115 | 0 | 1 | 2.807 | 10 | 0 |

The first pitch-hook execution falls from 232 to 211 instructions, from 2132 to 1972 modeled cycles, and from 1600 to 1480 instruction-fetch stall cycles. The full/fixed short-run margin improves from −2.227 µs to 2.807 µs. Context helpers also benefit from the smaller resolver.

The fixed-pitch control runs the helper but restores the original note. Its short pitch sequence matches stock-path playback; the full overlay matches the pitch-only control. Neutral-cost controls are diagnostic counterfactuals. Render-handler period overruns remain a separate metric from sample freshness and FIFO faults.

All runs have zero timing decoder mismatches, no halt, zero final core/timer gap, intact helper/table/guards and no unexpected guest writes to the watched reserved region. Every observed quantizer output matches the oracle and reads the copied table.

## Limits and next step

These observations depend on a 264 MHz core, 132 MHz bus, 48 kHz audio and assumed fill/writeback/beat costs of 40/32/8 cycles. The positive minimum margin is narrow. Finite tests do not establish physical timing, cache coherence or exclusive RAM ownership.

- Stock-path, sham and pitch-only controls restore stock instructions for playback from the same mod-initialized startup snapshot; they are not independent stock-loader boots.
- Full/fixed runs retain startup-installed helper bytes, hooks and initialized metadata. No reinjection of the helper or header.
- Cached-event context still uses the explicit diagnostic commit fixture.
- Clock, cache occupancy, memory costs, FIFO occupancy and phase are model assumptions; no physical cache-value simulation or measured device timing.
- Long workload is 1.04 seconds with eight keyboard buttons held; button count is not proof of worst-case simultaneous synthesis voices.
- Pattern requests do not prove completed pattern replacement.
- Finite preservation observations do not prove exclusive RAM ownership.

Next: seek more timing margin in the repeated context path and test heavier sustained-note/pattern-transition workloads. The cached-context producer fixture and physical cache/coherence questions still need resolution before treating this as hardware-ready.
