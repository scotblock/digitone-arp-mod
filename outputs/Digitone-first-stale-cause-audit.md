# Digitone OS 1.42: first stale read isolation

The changed pitch is excluded as the cause of this first stale read in the PC model. Full helper execution reproduces it even when the outgoing pitch is restored to stock. The failure is a combined timing effect: context hooks shift scheduling, then the first pitch-processing path exhausts the remaining sample-write margin. Modeled instruction-fetch delay is a decisive contributor. Firmware remains unchanged.

## Controls

Every case replays the same first 80 ms of the previous workload: initial 10 ms, pattern-2 request, PLAY press/release, then playback through 80 ms. The first stale read precedes the later keyboard-heavy section. Assumptions remain 264/132 MHz, 48 kHz audio, and fill/writeback/beat costs of 40/32/8 cycles. Original source bytes are unchanged; modifications and diagnostic fixtures exist only in guest RAM.

| Case | Stale reads | Minimum observed write margin (µs) | Margin at the previously failing stereo read (µs) |
|---|---:|---:|---:|
| Stock | 0 | 32.837 | 130.080 |
| Stock-instruction detour | 0 | 32.458 | 129.561 |
| Stock + changed pitch | 0 | 32.837 | 130.080 |
| Full hooks + stock pitch | 1 | -0.587 | -0.587 |
| Full hooks + changed pitch | 1 | -0.587 | -0.587 |
| Context hooks; stock pitch path | 0 | 11.545 | 11.545 |
| Full hooks; helper memory costs removed | 0 | 25.023 | 126.064 |
| Full hooks; helper computation costs removed | 0 | 21.655 | 21.655 |
| Full hooks; helper fetch delays removed after first pitch entry | 0 | 8.133 | 8.133 |

Stock + changed pitch delivers the same first three coarse pitches as the full modified case. Full hooks + stock pitch delivers the stock sequence. These reciprocal controls show that changing 57 to 56 does not cause the miss, while restoring 57 does not remove it. The full and fixed-pitch controls reproduce the same capture and following-store cycles.

The previously failing 8-byte stereo read covers SRAM 0x80001b00–0x80001b07. The capture observer records core cycle 16,722,874 and the next final-word store at 16,723,029: 155 cycles (0.587 µs) later. Its timer-derived log time is 63.333784 ms; the corresponding core-clock observation is 63.344220 ms. Timer stamps can lag inside a basic block, so cycle comparisons are used for margins.

## Scheduling and cost attribution

The native transport-state write at 0x400937c2 occurs 1259.371 µs later with full hooks than stock. First note acceptance moves from core cycle 16,374,780 to 16,551,004, a 667.515 µs shift, approximately one 666.667 µs audio block. Context-only has the same acceptance phase as full hooks, but its target read remains fresh by 11.545 µs. Adding the pitch path moves the following store 3,207 cycles (12.148 µs) later and produces the miss.

The first pitch-entry-to-output interval is 2,758 modeled cycles (10.447 µs), covering 370 instructions:

- Instruction-fetch charges: 1,960 cycles (7.424 µs); 1,440 are in helper RAM and 520 in called stock code and the continuation.
- Data fill and dirty eviction: 40 + 32 cycles.
- Block computation, stalls and flow: 726 cycles; 500 in helper RAM and 226 in stock code.
- The quantizer calls the existing scale-membership routine at 0x40106b6c three times. No nested interrupt appears within the measured pitch interval.

This interval accounts for the pitch path itself; the larger difference at the sample store also includes downstream cache/bus and scheduling effects. The components are not interchangeable or simply additive across counterfactual runs.

The targeted fetch control removes helper instruction-fetch delays only from the first pitch entry onward. It leaves the earlier context-hook scheduling shift and the exact first acceptance cycle intact, while preserving cache tag/dirty-state updates. The target read becomes fresh by 8.133 µs. This directly ties the failure to instruction-fetch timing on the critical path rather than to pitch value or earlier phase shift alone. Removing all helper memory delays or helper computation costs also prevents the miss.

## Limits and next step

- PC-only timing model with assumed clocks/costs, basic-block accounting and word-level DMA; not a measured hardware fault.
- Zero-cost memory/compute/fetch ablations are diagnostic counterfactuals, not implementable firmware fixes.
- Cache tags and dirty-state updates remain in memory/fetch-neutral cases; charge and bus-reservation effects are removed.
- Valid metadata is explicitly injected at commit for this cached-arp timing fixture; natural cached-context capture remains unproven.
- The controls isolate this first read over the exact first 80 ms; they do not certify later workloads, boot, storage ownership or physical cache coherence.

Next: reduce and bound the first-note pitch path’s instruction footprint and repeated scale-membership work in the PC prototype, then rerun the same stock/fixed-pitch controls and longer active playback. Merely warming a cache for free is not a valid implementation. Physical timing costs still require independent evidence.
