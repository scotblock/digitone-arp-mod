# First fresh receiving-pattern note: timing isolation

Removing the first fresh note’s 1,360 modeled helper-fetch cycles eliminates the smaller stale capture. The larger stale capture remains: fetch delay is a measured contributor, not a complete explanation. Firmware remains unchanged.

Exact original timing reproduced: True. Control starts pitch processing at the same cycle: True.

| Run | Pitch interval (cycles) | Interval (µs) | Removed fetch cycles | Stale captures |
|---|---:|---:|---:|---:|
| trace | 2037 | 7.716 | 0 | 2 |
| pitch-fetch-neutral | 677 | 2.564 | 1360 | 1 |

Both controls execute the actual uninterrupted native pattern handoff and consume receiving event 0x4199dc44 / generation 13. The incoming and outgoing note is 57 in both. No event eligibility or context metadata is injected at acceptance. The control removes fetch charges only while the pitch hook executes in the 2619–2625 ms diagnostic window; the preceding producer/context path remains charged.

Measured helper fetch charges within the traced pitch interval: 1360 cycles; helper data charges: 72 cycles. Active interrupt-vector sets: [(191,)]. The complete instruction/block and memory trace is retained in the individual run reports.

Measured helper computation/flow/stall block cost excluding its instruction fetches: 426 cycles. Interval attribution residual: 0 cycles; any residual is kept explicit rather than assigned to the helper.

## Missed writes

- 0x80001b00: next CPU store occurs 5511 cycles (20.875 µs) after capture; store PC 0x40096c26.
- 0x80001b04: next CPU store occurs 5511 cycles (20.875 µs) after capture; store PC 0x40096c2c.
- 0x80001b08: next CPU store occurs 64 cycles (0.242 µs) after capture; store PC 0x40096c26.
- 0x80001b0c: next CPU store occurs 64 cycles (0.242 µs) after capture; store PC 0x40096c2c.

Fetch-cost removal changes subsequent scheduling and bus contention as well as elapsed helper time. It demonstrates a contribution to the smaller capture failure, while leaving the larger failure unresolved. It does not identify a unique silicon defect or prove that every excess cycle belongs to the hook.

- 264/132 MHz and cache/bus costs are uncalibrated assumptions.
- The fetch-neutral control preserves instruction execution, cache tags and data costs but removes selected instruction-fetch delays/reservations. It is a diagnostic, not an implementable firmware change.
- Clock costs and interrupt delivery are basic-block granular; adding trace boundaries can alter translation. Exact reproduction is checked explicitly.
- Captures and following stores do not establish physical codec output or cache-value coherence.

The window contains the fresh track-2 pitch call followed by two other pitch calls. The latter calls have zero fetch charges in both runs, so all 1,360 removed cycles belong to the first call. Both later calls still take 122 cycles, and all three pitches match between controls.

## Downstream scheduling

After the first pitch output, the render executes the same instruction-block sequence when the nested audio-completion interrupt is excluded. The first sequence divergence is the position of vector 174 at the stock loop starting at `4009a2d6`. No nested interrupt occurs inside the measured first pitch interval; vector 174 does occur later before the sample writes.

The control saves 1,360 pitch-fetch cycles, but later block/fetch costs increase by 194 cycles and other downstream costs by 61 cycles. The first mixer write therefore advances only 1105 cycles (4.186 µs). Its remaining capture lateness is 4,430 cycles (16.780 µs). Both runs execute 74,372 observed downstream instructions before that store.

The inherited stock comparison consumes the same event/generation earlier: acceptance is shifted by 529059 cycles (2004.011 µs), and pitch-entry observation by 530789 cycles (2010.564 µs). Entry stamps include basic-block precharging and are not isolated function costs. This earlier phase shift remains in both diagnostic controls; its specific cause is not proved here.

Next: compare the matching stock render interval and its interrupt/cache phase, then separate the earlier context-processing shift from downstream memory cost. Do not assume another pitch-only reduction will close the larger gap.

## Independent local cost test

With an explicitly constructed valid context and no scheduler or DMA, the cold hook takes 3,054 modeled cycles: 1,760 instruction-fill cycles, 960 data-fill cycles and 334 other cycles. Self-warmed execution settles at 334 cycles. The scale lookup itself accounts for 651 cold cycles (531 block/fetch plus 120 data); validation and context-reading work account for the rest of the helper path. These are separate local fixtures and are not substituted for the actual playback trace.
