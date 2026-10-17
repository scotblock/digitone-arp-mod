# Digitone OS 1.42: cycle-aware checks from loader-derived startup

The timing suite completed from the executed-loader startup snapshot. The previous timing pass is not robust to this starting state: the full mod has a stale sample read under the adverse clock/memory assumptions. Functional table reads and code/storage preservation pass; physical hardware behavior remains unverified.

## Principal result

| Case | Duration (ms) | Captures with stale words | Late final-word stores | Minimum margin (µs) | Render-handler period overruns | FIFO faults |
|---|---:|---:|---:|---:|---:|---:|
| prefix-stock | 80.031 | 0 | 0 | 30.481 | 1 | 0 |
| prefix-sham | 80.031 | 0 | 0 | 30.216 | 1 | 0 |
| prefix-pitch-only | 80.031 | 0 | 0 | 30.481 | 1 | 0 |
| prefix-fixed | 80.021 | 1 | 1 | -2.227 | 1 | 0 |
| prefix-full | 80.021 | 1 | 1 | -2.227 | 1 | 0 |
| prefix-context-only | 80.021 | 0 | 0 | 6.076 | 1 | 0 |
| prefix-memory-neutral | 80.021 | 0 | 0 | 14.322 | 1 | 0 |
| prefix-compute-neutral | 80.021 | 0 | 0 | 5.477 | 1 | 0 |
| prefix-fetch-neutral | 80.021 | 0 | 0 | 3.246 | 1 | 0 |
| long-stock | 1040.105 | 0 | 0 | 30.481 | 8 | 0 |
| long-fixed | 1040.105 | 1 | 1 | -2.227 | 10 | 0 |
| long-full | 1040.104 | 1 | 1 | -2.227 | 11 | 0 |

The fixed-pitch control executes the full helper and restores stock output pitch. Its short pitch sequence matches the stock-path control; the full mod sequence matches the pitch-only control. Memory/compute/fetch-neutral cases deliberately remove costs and are diagnostic counterfactuals, not viable firmware solutions. Handler period overruns are distinct from stale sample data and FIFO faults.

The first late full-mod read is at 78.010799 ms: two stale stereo words at 0x80001b00. Its final store arrives 588 modeled core cycles (2.227 µs) after the capture observer. First native pitch-helper execution takes 2132 modeled cycles and 232 instructions. The widened trace window reproduces the untraced full run exactly.

## Continuity and functional checks

All cases restore the same loader-derived settled-UI snapshot, checked by its hash. The full and fixed-pitch cases retain the startup-installed hooks, 2,324 helper/table bytes and initialized metadata. The same extended flash contents are supplied for application asset reads. Stock-path controls remove selected hooks only in PC memory; sham adds a diagnostic detour.

Every observed quantizer result matches the pitch oracle, and every quantizer call has a native lookup read from the copied table. Helper bytes and guards remain intact, unexpected reserved-storage writes are absent, timing decoder mismatches are zero, and the final core/timer gap is zero. The original SysEx hash is unchanged.

## Interpretation and limits

The short full and fixed-pitch results show that the changed pitch is not required for the failure in this workload. The clean stock-path and sham controls implicate added helper/context execution or its scheduling/cache effects. Neutral-cost cases further constrain that explanation; no physical timing conclusion follows from them.

These runs assume a 264 MHz core, 132 MHz bus, 48 kHz audio frames and cache-fill/writeback/DMA-beat costs of 40/32/8 cycles. The timing model starts with empty caches rather than the physical cache contents produced by startup. A failing sensitivity model is a reason to improve the margin and model evidence, not proof that the physical Digitone would fail.

The short full-mod sensitivity run with lower fill/writeback/beat costs of 20/16/4 cycles has no stale reads, no handler period overruns and 169.841 µs minimum observed margin. Neither cost set is a hardware measurement; this result establishes sensitivity to the assumptions.

The cache-occupancy model uses four ways, 128 sets and 16-byte lines for each 8 KB cache, following the explicit organization in §6.2 of the [NXP MCF5441x Reference Manual](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf). Its replacement, cost and state approximations remain PC modeling assumptions.

- Stock-path, sham and pitch-only controls restore stock instructions for playback from the same mod-initialized startup snapshot; they are not independent stock-loader boots.
- Full/fixed runs retain startup-installed helper bytes, hooks and initialized metadata. No reinjection of the helper or header.
- Cached-event context still uses the explicit diagnostic commit fixture.
- Clock, cache occupancy, memory costs, FIFO occupancy and phase are model assumptions; no physical cache-value simulation or measured device timing.
- Long workload is 1.04 seconds with eight keyboard buttons held; button count is not proof of worst-case simultaneous synthesis voices.
- Pattern requests do not prove completed pattern replacement.
- Finite preservation observations do not prove exclusive RAM ownership.

Next: isolate and reduce the added context/pitch execution costs using the measured failing interval, then rerun stock-path/full/fixed controls from this same loader-derived state. Firmware remains unchanged and no flashable image was produced.
