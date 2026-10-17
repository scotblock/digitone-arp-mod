# Digitone OS 1.42: revised startup, handoff and timing verification

**The revised helpers now survive actual PC loader/startup execution. A fresh receiving-pattern arp note and an older queued arp note use their respective scales during one uninterrupted handoff. Timing remains conditional on model assumptions.** Device firmware is unchanged.

The ephemeral loader fixture contains the 2,564-byte helper image plus both cache-copy call-site hooks. The stock loader accepts/decompresses it, and its machine state continues into application initialization. The early copier copies 641 longwords; the initializer establishes the owner pointer and ready header. Cold, intro and settled stages preserve the complete helper image and guards, with no unexpected reserved-region writes. Playback/handoff/timing restore those guest snapshots and verify both hooks; no helper or header is reinstalled by the host.

The basic inherited-startup control publishes an old-scale event at 248.667 ms, completes replacement at 2669.837 ms and accepts the same generation at 3168.667 ms. It retains `0x800040bd` and outputs 56.

## Fresh and old notes in the same transition

Native panel copy/paste prepares an arp-enabled receiving pattern while stopped, including its associated settings. The playback test then starts and performs a complete pattern-2 → pattern-1 replacement without stopping the transport. Direct backing-data cloning and an additional MIDI probe did not establish the eligible fresh-note case; neither is counted as a positive witness.

| Witness | Event/generation | Context | Input → output | Time |
|---|---|---|---|---|
| Fresh receiving-pattern arp input | `0x4199dc44` / 13 | `0x8000433b` | 57 → 57 | 3858.667 ms |
| Fresh receiving-pattern arp continuation | `0x4199dc44` / 15 | `0x8000433b` | 69 → 69 | 4021.333 ms |
| Older queued arp input | `0x4199dadc` / 1 | `0x800040bd` | 57 → 56 | 4148.021 ms |

Replacement completes at 3669.858 ms. The direct fresh event is constructed afterward from receiving backing `0x407b00cc`, track 2, root 59/raw scale 5, and carries `0x8000433b` through publication and native quantization. The older event was published from backing `0x407c61e9`, root 61/raw scale 0, before replacement and arrives later with `0x800040bd`. Same event/generation and execution-order matches establish the witnesses; no eligibility, identity or context metadata is supplied at acceptance.

## Timing controls

Assumptions: 264 MHz core, 132 MHz bus, 48 kHz audio, normal fill/writeback/beat costs 40/32/8. These are modeled costs, not physical measurements. Acceptance-time context injection is disabled in every case. The fixed-pitch control runs the helper path then restores the stock pitch as a diagnostic.

| Case | Duration | Native quantizations | Stale DMA captures | Minimum margin | Handler-period overruns |
|---|---:|---:|---:|---:|---:|
| prefix-stock | 80.031 ms | 0 | 0 | 30.481061 µs | 1 |
| prefix-fixed | 80.021 ms | 1 | 0 | 4.375000 µs | 1 |
| prefix-full | 80.021 ms | 1 | 0 | 4.375000 µs | 1 |
| sustained-stock | 1840.156 ms | 0 | 0 | 30.481061 µs | 12 |
| sustained-full | 1840.125 ms | 8 | 0 | 4.375000 µs | 13 |
| sustained-full-slow-memory | Incomplete | 0 | Inconclusive | Inconclusive | Inconclusive |
| sustained-stock-slow-memory | Incomplete | 0 | Inconclusive | Inconclusive | Inconclusive |

The doubled memory-cost controls (80/64/16) both stop on `DMA restart while modeled transfer is active`, at the same workload boundary and last audio-capture timestamp, before any observed cache-copy call or quantization. This exposes a DMA-model limit and leaves the sensitivity check inconclusive. Positive normal-cost results do not establish timing safety across that range. Handler-period overruns and capture margins measure different boundaries; zero stale captures is not a claim that every handler finishes within one nominal period.

## Next step

Resolve active-transfer restart behavior in the software DMA model, then rerun the sensitivity pair. A cycle-aware complete pattern handoff should also be measured; it has so far been exercised functionally, separately from voice-heavy timing. Physical timing/cache coherence and exhaustive ownership remain unverified, so these results do not justify flashing the device.
