# Digitone OS 1.42: DMA configuration and self-link arbitration

## Finding

The firmware explicitly enables round-robin channel arbitration. With documented hardware reset values, minor-loop self-links must re-enter arbitration; they cannot run as an uninterrupted series of minor loops. The existing timestamped PC engine does not implement that shared controller selection. A controlled two-channel test demonstrates this limitation.

The sampled playback workload had no overlapping software-started DMA channels. This explains why that particular contention defect did not cause failures there. Audio DMA uses a separate emulator path, so its competition with software DMA remains untested by the current model. Earlier render margins remain results of that model, not hardware timing guarantees.

## Firmware configuration evidence

At `0x40000546..0x40000552`, unchanged MAIN OS instructions load the DMA control address `0xfc044000`, read its value, OR it with `0x6`, and write it back. This sets ERCA (round-robin channel arbitration) and EDBG. It preserves CLM, ERGA, group priorities, EMLM and other inherited fields.

Native execution of that exact instruction slice passed five inherited-state cases, including CLM set and clear. The operation consistently preserves CLM; it does not explicitly force it off.

A separate MAIN OS startup trace seeded the documented DMA reset values: CR=`0xe400` and DCHPRI byte n=`n`. Across approximately 180 million estimated instructions, ten tasks were created and the run reached the startup waiting loop at `0x4008cb0e`. The only observed write to CR or channel priorities was:

`PC 0x40000552: [0xfc044000] = 0xe406`

All seeded priority bytes remained intact. This is bounded PC execution from MAIN OS entry, with supplied boot flags `0x00140000`, the synthetic card and existing emulator helpers. It is not a physical-device trace or a full serial-boot handoff proof.

The separate bootstrap trace preserved the seeded DMA configuration through approximately 30 million estimated instructions but stopped at its limit before entering MAIN OS. Full bootstrap-to-application inheritance remains unverified. A literal scan found the MAIN startup reference to CR and no literal references to DCHPRI in the scanned bootstrap/MAIN images; computed accesses are not excluded by that scan.

## Meaning of the documented reset configuration

For the seeded startup result `0xe406`:

| Field | Value | Consequence |
|---|---:|---|
| CLM | 0 | Self-links return to arbitration between minor loops |
| ERCA | 1 | Channels rotate within each group |
| ERGA | 0 | Highest-priority requesting group wins |
| Group priorities 0, 1, 2, 3 | 0, 1, 2, 3 | Group 3 has highest priority |
| EMLM | 0 | Standard NBYTES interpretation |

Preemption is available only with fixed arbitration for both group and channel selection. A newly requesting channel therefore waits for a minor-loop boundary in this configuration. The final minor loop uses major-loop linking rules rather than emitting another minor self-link. These meanings come from the [NXP MCF54418 reference manual, chapter 19](https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf#page=366), particularly sections 19.4.1, 19.4.16, 19.6.3.4 and 19.6.6.

This decoded configuration is conditional on the documented reset state surviving the earlier boot path. MAIN OS's explicit OR operation and its preservation behavior are directly verified.

## Snapshot discrepancy

All three existing saved emulator snapshots contain CR=`0x6` and 64 zero priority bytes. That differs from the documented reset configuration. In particular, their group priorities are all zero despite fixed group arbitration being selected. The current emulator does not enforce the resulting priority-configuration error.

These snapshots therefore cannot supply trustworthy inherited hardware priority settings. No snapshots were rewritten in this audit. Proper reset initialization and faithful priority readback belong in the controller model; silently assuming the saved zeros are the device's settings would be incorrect.

## Live workload observations

A stock run repeated the prior pattern-2 workload with 100 ms of active playback, approximately 280 ms including preparation and stopping:

- 1,677 software DMA starts; none began with another software channel active.
- 211,659 completed minor-loop boundaries; none had another software channel active.
- No observed guest writes to CR or channel priorities; CR remained `0x6` in this snapshot-based run.
- 16,341 fetched scatter/gather descriptors; none had major-link enable set or a CITER/BITER link-enable mismatch.
- Sampled self-links included channel 47 with 64/58 iterations, channel 30 with 17/13/9 iterations, and channel 42 with 16 iterations. Their minor-loop size was 16 bytes.
- No engine halt or decoder mismatch, 419 completed renders, and no late or stale captured audio frames under the existing timing assumptions.

Those absence findings apply to this finite stock software-channel trace. They do not cover all inputs, the full-hook workload, or pending requests handled by other peripheral models.

## Controlled counterexample

With CR explicitly set to `0xe406`, channels 42 and 47 were each given a three-iteration self-linked descriptor and started before servicing payload events. The current engine immediately marked both ACTIVE. When events were serviced every cycle:

| Event | Modeled cycle |
|---|---:|
| Channel 42 first source read | 4 |
| Channel 47 first source read | 8 |
| Channel 42 first destination write | 12 |

Channel 47 reads before channel 42 completes its first minor loop. The model serializes individual bus reservations, but lets separate channel generators progress concurrently. That is not a shared, non-preemptive eDMA controller. Both final payloads are correct; temporal arbitration is the defect demonstrated here. It is independent of the previous block-boundary service-lateness limitation because this fixture services events every cycle.

## Audio competition and next implementation

The restored Session's selected SSI profile uses receive channel 52 and transmit channel 54. Its programmed descriptors use 8-byte minor loops, 64 iterations and half/major completion interrupts; transmit reads `0x80001a00` and writes SSI1 at `0xfc0c8000`. Both channels are in group 3. Observed software channels 42/47 are in group 2 and channel 30 is in group 1.

Under the documented reset group priorities, pending audio requests can win at software self-link arbitration boundaries. The current frame-level SSI path never enters a common request queue with software DMA, so the software-only lack of overlap does not close this question.

The next implementation is one shared eDMA request queue and active-minor-loop owner for software and SSI channels. It should initialize/read back documented configuration, apply fixed group and rotating channel selection, retire/requeue self-links only at the appropriate boundaries, and distinguish final-minor completion from further self-linking. Test audio requests arriving during a software minor loop, same-group competitors, CLM set/clear, final iterations, scatter/gather transitions and completion publication before repeating the matched playback comparison. Arbitration latency remains a separate hardware-calibration question; no arbitrary latency constant was added here.

The production timestamped DMA model was left unchanged during this audit. The new scripts are diagnostic observers and isolated fixtures. No firmware image was modified or produced, and no hardware was accessed.

## Saved evidence

- `Digitone-DMA-self-link-audit-summary.json`: combined assertions and scope.
- `Digitone-DMA-startup-config-native.json`: five native instruction-slice cases.
- `Digitone-DMA-main-startup-config-trace.json`: bounded startup writer trace.
- `Digitone-DMA-bootstrap-config-trace.json`: bounded pre-OS trace.
- `Digitone-DMA-configuration-clues.json`: saved snapshot settings and literal scan.
- `Digitone-DMA-runtime-configuration.json`: complete stock workload observations.
- `Digitone-DMA-arbitration-counterexample.json`: timed two-channel counterexample.
- `Digitone-DMA-SSI-profile-check.json`: selected SSI channels and descriptors.

Verified unchanged SHA-256:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- MAIN OS: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`
