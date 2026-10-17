# Matching stock and prototype render: phase versus cost

Both runs restore the same prepared guest snapshot, use the same workload and disable HLE. The stock control restores all seven hook sites. The prototype reproduces the preceding diagnostic exactly. Firmware remains unchanged.

The older comparison used different preparation end times. The raw timer “now” difference is 42,666 ticks at 64 MHz (0.666656 ms); the standard timed restore rescales this phase by 264/64 with an unchanged 132 MHz bus, giving 175,997.25 core cycles. The new pair removes that starting-state confound.

| Measurement | Stock | Prototype | Difference |
|---|---:|---:|---:|
| Matched render start (cycles) | 692201662 | 692201663 | 1 |
| Render start → first output write (cycles) | 179896 | 186581 | 6685 |
| Instruction fetch charges (cycles) | 64428 | 68757 | 4329 |
| Data memory charges (cycles) | 15840 | 16250 | 410 |
| Nested interrupt entry charges (cycles) | 18 | 18 | 0 |
| Explicit accounting residual (cycles) | 0 | 0 | 0 |
| Stale captures after 20 ms | 0 | 2 | 2 |

The first output write moves by 6,686 cycles. This separates exactly into a 1-cycle render-start shift plus 6,685 cycles of additional elapsed work after that start. The within-render difference comprises 4,329 instruction-fetch cycles, 410 data-memory cycles, 1,946 computation/flow/stall block cycles, 0 nested interrupt-entry cycles and 0 explicitly unassigned cycles.

Both runs consume event 0x4199dc44 / generation 13 and output note 57. The first output buffers are 0x80001b00 and 0x80001b00; each is matched to its own render frame and first subsequent DMA capture. Observed write margins are 4.345 µs (stock) and -20.875 µs (prototype). Positive margin alone does not prove every sample is fresh; the capture freshness flags and full-workload counts are preserved in the summary.

The complete 72-byte event at pitch entry is identical in both runs. Overlay-RAM instruction fetches account for 3,640 added cycles; fetch charges outside that overlay rise by a further 689 cycles. Overlay code also executes displaced stock instructions, so region totals are not a count of purely new work. Fetch, data, flow and stall costs remain distinct.

The earlier roughly 2 ms pitch-entry shift does not survive the shared-start comparison: matched render starts differ by one cycle. The remaining observed regression is work within the render, including the broader context hooks and downstream memory effects. The preceding fetch-neutral control isolated 1,360 pitch-fetch cycles and removed one capture; optimizing only that pitch fetch path does not address the entire 6,685-cycle within-render difference.

## Limits

- 264/132 MHz, 48 kHz audio and memory costs remain assumptions.
- One shared prepared guest state; stock control restores seven hook sites while retaining unused helper RAM. This isolates runtime instruction changes, not a fresh physical stock boot.
- Cycle costs and write observations are basic-block granular; costs are observational intervals, not silicon measurements.
- First buffer address may differ between logically matching render blocks; capture comparisons use the first write target belonging to each matched frame.
- Any accounting residual is retained explicitly.

Next: reduce the combined context/pitch hot path’s instruction footprint while preserving its validations, then rerun this shared-state pair. Fetch charges dominate the measured difference, but this accounting does not uniquely assign every downstream miss to one helper or certify physical timing.
