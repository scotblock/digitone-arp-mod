# Digitone OS 1.42: indexed context processing and extended coverage

The repeated event-slot walks were replaced by a bounded index calculation in the PC-only overlay. No cached pointer, new metadata or additional RAM state was introduced. The original firmware and executable files remain unchanged; no installable image was generated.

## Implementation and checks

A shared 34-byte helper checks the unsigned offset from the 128-event pool, divides by the 72-byte stride, rejects a non-zero remainder and returns the candidate-array offset. The 9,216-byte bound keeps the 16-bit quotient below 128 and avoids divide overflow. It occupies previously unused executable padding in the copied helper image. Snapshot reading and candidate storing call it instead of walking the pool. Every store still checks the original complete header, and the pitch/retained-context validation is unchanged.

All helper entry addresses, startup copying, lookup-table bytes and total 2,324-byte overlay length are preserved. Snapshot/store bodies shrink from 60/70 bytes to 36/42 bytes.

Native tests pass all 9,216 pool byte offsets, 646 snapshot/store pointer comparisons, five invalid-header cases, forty commit-trampoline ABI comparisons, six allocator-return comparisons (including allocation failure), and the existing four-track hook tests. The trampoline tests compare all registers, materialized SR flags, event bytes and context storage. A fresh executed-loader startup, initialization and playback also pass.

The index calculation has bounded work. At slot 127, snapshot instructions fall from 771 to 19, and store instructions from 802 to 50; an out-of-pool pointer avoids the complete failed walk. It has a tradeoff: at slot zero, the short old walk used fewer instructions (9 versus 19 for snapshot). The playback measurements below test the aggregate effect rather than assuming every individual call becomes faster.

## Cycle-aware timing and longer sustained notes

| Control | Duration ms | Stale captures | Minimum margin µs | Render period overruns | FIFO faults | Native quantizer calls |
|---|---:|---:|---:|---:|---:|---:|
| prefix-stock | 80.031 | 0 | 30.481 | 1 | 0 | 0 |
| prefix-fixed | 80.021 | 0 | 13.572 | 1 | 0 | 1 |
| prefix-full | 80.021 | 0 | 13.572 | 1 | 0 | 1 |
| sustained-stock | 1840.156 | 0 | 30.481 | 12 | 0 | 0 |
| sustained-full | 1840.115 | 0 | 6.091 | 13 | 0 | 8 |

The full/fixed short-run minimum margin rises from 2.807 µs to 13.572 µs. The stock-path short run exactly repeats the previous DMA captures, transport trace, delivered pitches and render results. Full/fixed pitch sequences provide the same stock-pitch diagnostic control as before.

The extended full run reaches a tighter 6.091 µs minimum margin later in playback, with no stale captures or FIFO faults. This is the minimum for the longer workload; the short-run 13.572 µs margin does not describe the entire run.

The held-note interval doubles from 800 to 1,600 ms, with eight keyboard buttons pressed, followed by release and stop. Thirty-two allocation-mask observations replace the previous sixteen. Allocation bits and button count do not establish the physical worst-case voice workload.

All timing cases have zero decoder mismatches, no halt, zero final core/timer gap, matching native table reads and oracle outputs, intact code/table/guards and no unexpected watched guest storage writes. The active cached-event context is still supplied by the explicitly labeled diagnostic commit fixture in these timing runs.

## Confirmed native pattern and MIDI-sustain handoff

Four native functional runs compare stock-path/full playback with existing pattern settings and with explicit old/new root-scale settings. The stock transition writer at 0x40095926 changes backing 0x407b00cc to 0x407c61e9, execution reaches completion at 0x40095bd6, and subsequent notes consume the receiving backing. This confirms a completed replacement rather than only a queued panel request.

One actual stock-produced event is deliberately delayed by 48,000,000 queue ticks. It remains pending at replacement and is accepted afterward with the same event address and allocation generation. In the scaled full run its captured old-context word 0x8000033b is still present at acceptance. The crossing event is a direct note with zero identity; its old-scale arp eligibility is not proved.

MIDI CC64 travels through the modeled UART receive/parser and stock controller handler. Sustain is enabled and the held-note list is non-empty at the actual replacement; CC64 release later clears both. Input bytes and MIDI receive enable are explicit PC fixtures.

The scaled run sets the old pattern to root 59/raw scale 5 and the receiving pattern to root 61/raw scale 0. Candidate and retained metadata are not injected in these functional runs. Eleven receiving-pattern arp results match the oracle, including 57→56, 69→68 and 81→80. Quantizer calls are paired to actual outputs using event address, allocation generation and execution order, rather than coarse functional timestamps. Helper/table/guard preservation passes in all four runs.

## Limits and next step

The cycle-aware model still assumes 264/132 MHz clocks, 48 kHz audio and 40/32/8-cycle fill/writeback/beat costs, with empty modeled caches at playback. Render-period overruns remain distinct from stale audio reads and FIFO faults. Physical timing, cache-value coherence and full RAM ownership remain unverified.

The longer cycle-aware playback and the native functional transition are separate experiments. This does not certify timing through an actual pattern replacement, nor does the direct queued-note crossing prove that an eligible old-pattern arp note uses its original scale afterward.

Next: exercise an eligible queued arp-note crossing with native context capture, then measure a confirmed transition under the cycle-aware model. No hardware installation is supported by these results alone.

