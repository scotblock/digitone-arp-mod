# Digitone OS 1.42: shared software/audio DMA controller

The PC engine now routes software DMA self-links and SSI audio requests through one controller. A channel retains ownership across all source reads and destination writes of a minor loop. At an eligible self-link boundary it releases ownership and re-enters arbitration. Competing audio requests can then win according to the DMA configuration. Payloads remain timestamped; they are not copied eagerly at launch.

## Implementation and scope

The isolated module is `work/shared_dma_arbiter.py`, used by the PC comparison runner. Existing timestamped and upstream DMA implementations remain available as baselines. Firmware files and device hardware were not changed.

The controller reads CR, uses fixed or rotating group selection and fixed or descending rotating channel selection, queues software and SSI requests, honors HALT, and bypasses arbitration for CLM-enabled intermediate self-links. Final minor completion does not emit an extra minor self-link. Scatter/gather transitions re-enter selection. Audio reads, writes, half-buffer flags, major completion and buffer wrapping occur as the granted transfer progresses. Simultaneous RX/TX requests emitted by the SSI service are queued together before selection.

The saved snapshots omit documented DMA reset priority fields. The PC setup explicitly restores those missing group/priority fields while retaining the snapshot's observed control flags, producing CR `0xe406` for this workload. This is a documented-reset modeling assumption, not a recovered physical-device state. The inherited bootstrap configuration remains unverified.

The exercised software descriptors self-link to their own channel. Unsupported cross-channel software links, multi-iteration unlinked software descriptors, EMLM, software major links and enabled fixed-priority preemption are rejected rather than silently approximated. The model does not route every peripheral DMA implementation through this controller.

## Focused verification

Twenty controlled checks passed. They cover single ownership; same-group rotation; audio waiting for the active minor loop and winning at its boundary; CLM bypass; correct payload and timed source capture; queued ACTIVE state; half/major completion and wrapping; scatter/gather re-arbitration; halt/resume; invalid fixed priorities; and drained queues. A separate native guest SSRT/CSR polling fixture waits for the final write, observes correct completion and payload, and drains the controller. That fixture made 61 deferred polls and reached completion at cycle 171.

## Matched longer comparison

Each variant uses the same settled stock snapshot and synthetic card, pattern 2 and one second of active playback. Preparation and stopping bring total coverage to approximately 1.180 seconds per run. This is a snapshot-resumed workload, not a cold-boot validation.

The full-hook variant uses runtime RAM overlays and an injected candidate root/scale metadata context for the existing capture/copy gap. Its pitch checks therefore validate that fixture path, not all natural live-context producers.

Assumptions remain 250 MHz, 20 cycles per cache-line fill, 16 per dirty writeback, and four cycles per four-byte DMA/uncached beat. The shared bus is serialized. No calibrated arbitration overhead has been added.

| Variant | Renders | Worst render µs | Deadline margin µs | Late renders | Stale audio captures | Dropped audio requests | Grants with competitors |
|---|---:|---:|---:|---:|---:|---:|---:|
| stock | 1,769 | 581.160 | 85.508 | 0 | 0 | 0 | 62,676 |
| all | 1,769 | 596.472 | 70.196 | 0 | 0 | 0 | 62,657 |

- **stock**: 113,308 audio minor requests; 113,306 completed audio minors; maximum payload-event service lateness 205 assumed cycles. End-of-test owner: `54`; waiting channels: `[52]`; active/incomplete channels: `[52, 54]`.
- **all**: 113,314 audio minor requests; 113,312 completed audio minors; maximum payload-event service lateness 206 assumed cycles. End-of-test owner: `54`; waiting channels: `[52]`; active/incomplete channels: `[52, 54]`.

Active transfers at the finite boundary are included explicitly, and completed audio requests plus pending/active audio requests reconcile to the emitted request count. No dropped audio requests were observed. This does not establish a real codec FIFO deadline: SSI request arrival and interrupt delivery still happen at outer scheduler boundaries, and payload service uses block/memory boundaries.

All five target pitch outputs match the independent expected values: 57→56, 69→68, 81→80, 57→56, 69→68. Other observed tracks' pitch events match stock. Neither run halted or reported decoder mismatches. These results apply to the tested workload and retained-context fixture.

## Remaining limits and next step

Other peripheral DMA paths are outside the shared controller. SSI scatter/gather descriptor loading is still delegated to its baseline helper; the tested mk1 audio descriptors use direct half/major buffer wrapping. Unknown external RX audio bytes remain unchanged rather than being invented, while their transfer service is charged. A repeated SSI request arriving while its channel is already pending is counted as dropped; none occurred in these runs.

Queued descriptor fields are currently captured at request time, although payload source bytes are read when their granted beats execute. Pending descriptor edits are not fully modeled. Software progress registers are not fully updated per hardware beat. DCHPRI group readback is seeded rather than dynamically regenerated for every CR change. Cached byte values are not represented separately from memory. Actual core clock, DDR costs, arbitration latency, refresh, FIFO behavior and cache/DMA coherence remain uncalibrated. A passing PC comparison is not a hardware safety certification.

The next focused gap is scheduling SSI requests at their actual modeled request timestamps and handling completion interrupts at modeled transfer completion, then checking codec FIFO deadlines. Current timing margins must retain the scheduler and clock assumptions until that is done.

Arbitration semantics are based on the [NXP MCF54418 reference manual, chapter 19](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=366), particularly CR/CLM, channel priority and section 19.6.3.4.

## Evidence and preservation

Saved comparison: `Digitone-shared-DMA-arbiter-long-comparison.json`. Summary and pitch validation: `Digitone-shared-DMA-arbiter-long-summary.json`. Controlled checks: `Digitone-shared-DMA-arbiter-checks.json`. Native polling check: `Digitone-shared-DMA-native-poll-check.json`. The earlier short pilot preceded the final audio CSR status update; the longer run uses the completed implementation.

Implementation SHA-256: `b3d31bc7d977b09917d5ae858042de930105007165ee53755d0262def23adaf0`.

Original SysEx SHA-256: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`. MAIN OS SHA-256: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`. Both match the original files. No flashable firmware was produced.
