# Packed context and pitch comparison

The PC-only image shrinks from 2,564 to 2,212 bytes (352 bytes; 13.73%). The 535 retained instructions shrink from 1,888 to 1,784 bytes; an additional six-byte forwarding jump is bypassed. Padding is removed, transfers shortened and code/table pointers relocated. The 420-byte lookup table, context storage, checks, register saves and interrupt masks are preserved. Firmware remains unchanged.

## Behavior checks

Machine-code differential comparisons: 13,514. Additional tests cover cache producer invalidation and stock memcpy ABI, four actual producer/pitch hook interfaces, 40 outer commit cases, eight allocator-return cases and 20 begin/cancel continuation cases. A structural audit accounts for all 535 retained reachable instructions and the bypassed forwarding jump, and verifies 496 fallthroughs. These checks preserve the existing helper contracts; they do not expand proof of hardware ownership or startup safety.

Seven direct initialization/reset-entry cases also match, including bad-header, null-pointer and wrong-argument failure paths. These invoke the entry directly rather than proving the outer startup/shutdown route.

## Same-state timing comparison

The candidate restores the same prepared snapshot, verifies inherited code and hooks, then installs the relocated candidate only in PC RAM. It uses the same 264/132 MHz candidate, memory costs, native pattern handoff and audio probes as the completed stock/original controls. No timing-charge ablation or prewarming is applied. Controls are reused from their completed runs.

Panel command sequence, MIDI message bytes and delay fixture are verified against the reference. An earlier candidate replay enabled additional live-note inputs and is excluded from this comparison.

| Measurement | Stock | Original helper | Packed helper |
|---|---:|---:|---:|
| Render start, cycles | 692201662 | 692201663 | 692201660 |
| Start to first output write, cycles | 179896 | 186581 | 186634 |
| Instruction fetch charges, cycles | 64428 | 68757 | 68651 |
| Data access charges, cycles | 15840 | 16250 | 16396 |
| Observed first-write margin, cycles | 1147 | -5511 | -5551 |
| Stale captures after 20 ms | 0 | 2 | 2 |

Relative to the original helper, within-render work changes by +53 cycles (+0.201 µs). This comprises -106 fetch cycles, +146 data cycles, +13 computation/flow/stall cycles and +0 interrupt-entry cycles. Accounting residual is zero.

Compared with stock, the remaining within-render difference is +6,738 cycles (+25.523 µs). The packed first-write margin is -21.027 µs. The complete 72-byte event is identical in all three runs; event 0x4199dc44 / generation 13 uses retained context 0x8000433b and outputs note 57. Code and guards remain intact; no unexpected guest writes, decoder mismatches or modeled FIFO faults were observed.

The separate isolated cold producer/begin/success/commit/pitch sequence falls from 5,818 to 5,539 cycles (279 cycles). Its instruction-fetch charges fall by 280 cycles and data charges are unchanged. The isolated cold pitch alone stays at 3,054 cycles. These fixtures supply a successful selector result and execute no scheduler or DMA; they support cost investigation, not completed-handoff coverage.

## Limits

- 264/132 MHz and memory/DMA costs remain modeled assumptions, not measured silicon timings.
- Same prepared snapshot and input workload; completed stock/original controls reused without rerunning them.
- Candidate is explicitly installed in PC RAM before timed playback; no loader/bootstrap installation of the packed candidate has been tested.
- Only the seven playback hook destinations are retargeted in this focused replay. The inherited initializer hook at 0x400f0504 still refers to 0x47be0666; the relocated reset entry must be connected before startup/reinitialization coverage.
- Region ownership and physical cache coherence remain unproven.
- Block-granular clock/capture observations; one handoff and 2.63 seconds of playback coverage.
- Delayed source note remains queued beyond this focused replay; this run does not newly prove its later consumption.

Next: connect and test the relocated startup/reinitialization route; then isolate the remaining context/copy and downstream cache costs before another optimization. Passing this comparison would still not establish physical timing or readiness to flash.
