# V1 scale-locked arp: consolidated trial decision

Reviewed 7 October 2026. Target: original Digitone / Digitone Keys OS 1.44. Current candidate: E03, PC-only. This is an evidence review and scope decision, not a new firmware build or instruction to install it.

## Decision

Keep the tested arp behaviour. Do not add a USB receive-freeze subsystem to V1 at this stage. Evaluate the stock startup-menu updater over physical MIDI as the preferred first-trial installation route, subject to exact-image/route validation and a usable stock recovery path.

Three concrete pre-trial work packages remain: startup failure/continuity, RAM/code placement, and installation/recovery. Physical timing and cache execution remain trial risks requiring observations on a device; an emulator cannot prove them away. E03 is not ready to install today.

User-confirmed setup: physical Digitone currently runs OS 1.44, has a USB connection, and the computer has a Roland Rubix22 interface. Roland lists MIDI IN/OUT for Rubix22, so it supplies the required interface type for the proposed DIN route. A five-pin cable, working SysEx transfer and stock recovery have not yet been confirmed. Proposed connection: computer USB → Rubix22 → Rubix22 MIDI OUT → Digitone MIDI IN. The Digitone USB connection does not provide startup-menu transfer.

## Evidence we can rely on

| Area | What the existing evidence establishes | Limit |
|---|---|---|
| Scale mathematics | Isolated 1.44 quantizer checks agree with extracted firmware scale rows across 13,824 combinations. | Boundary/fixture testing, not every performance setting on hardware. |
| Context interfaces | 1.44 producer, selector, allocator, copy, commit and pitch interfaces have differential/ABI tests. Context follows allocation generations and tested copies. | Finite recovered paths; not universal event ownership. |
| Musical operation | Continuous 1.44 PC execution covers playback, sustain, cancellation and an actual pattern replacement. An eligible cached type-1 replay uses its original root/scale after replacement. | A separately delayed type-0 event is canceled by stock; it is not revived. Do not describe that as successful replay. |
| First-copy handling | Stock handler plus supplied state-3 status packet reaches both copy operations, acceptance and pitch output. | Natural hardware production of the status packet remains unverified. |
| Saved-session behaviour | Same-session outputs change 60,61,64,66,60 into 60,60,64,65,60 as intended. Matched simple/factory workloads have clean synchronous PCM controls. | Direct uploaded stock/modified WAVs use different settings; broad audio transparency is not proved. |
| Crackling diagnosis | Threaded DSP handoff reproduces the emulator crackling; host synchronization removes that discontinuity in the tested session. | Emulator host fix, not evidence about device timing. Earlier packet-age differences are model scheduling observations. |
| Container and flash footprint | E03 compact container passes independent checks and stock instruction decoding. Modeled erase/program bounds avoid observed stock-data regions; explicit final padding is included. | Physical geometry/write outcomes are fixtures. E02's oversized packaging is unsuitable and superseded by E03. |
| Boot prefix | E03 stock loader-derived state reaches the copier and stock clear/cache prefix with exact helper bytes. E02 application boot/playback exists; E03 has the same MAIN executable. | One uninterrupted exact E03 loader-to-full-application run remains a useful bounded check. Equal MAIN does not certify inherited physical state. |
| Ordinary receiver | Tested checksum, sequencing, completion, queue/action lifetime and simulated programming produce exact E03 contents. Primary USB software tests extend ingress coverage. | Explicit scheduling/peripheral fixtures; no device flash. |
| USB shutdown | Recent tests identify deferred work, gate writers, callback/cancellation ordering and a host replenish guard. | Guard is unimplemented. Full scheduler/hardware exclusion is not certified and is no longer the proposed V1 installation dependency. |

Do not count 1.42 timing/ownership studies as complete 1.44 coverage. Earlier reports' lists of next steps are historical; this decision sets the current scope.

## Three blockers before a hardware trial

### 1. Define and test startup failure behaviour

The current reset wrapper loops indefinitely at IPL7 on invalid startup header/argument/null pointer. A non-null pointer is dereferenced without a demonstrated address-bound check. Runtime pitch fallback does not resolve startup failure.

Required result: one explicit policy, preferably retaining stock startup/pitch behaviour when context metadata is unavailable, with pointer bounds and a tested continuation. That fallback is not implemented and may require restructuring initialization; do not assume a one-instruction change is enough. If executable code itself is damaged, recovery may require the stock startup updater rather than an in-process fallback.

Acceptance: valid startup, unavailable/bad metadata, invalid pointers and repeated initialization take documented paths; no unintended write or unexplained hang; exact candidate runs through loader, copier, full initialization and playback. Failure-path code must be reviewed with its stock continuation before producing the trial candidate.

### 2. Establish defensible RAM/code placement for 1.44

Current code/table occupy `47be0000..47be08a4`; pointer/header/context occupy `47be1000..47be1b74`. The occupied span is 7,028 bytes. The profile-backed reservation is `47be0000..47c00000`. Stock clearing misses it, and observed tests preserve it, but worst-case stacks, computed writes and DMA ownership are not sufficiently covered for 1.44.

Required result: a bounded, documented allocation/reservation argument, including known stacks, heap boundaries, DMA ranges and reset/project-load writers for this firmware. Watch traces are supporting evidence, not a substitute for the map. If the map conflicts or cannot be justified, use a different established allocation mechanism rather than endless tests of the same unowned address.

Acceptance: a reviewed memory map and startup/cache-handoff rationale, plus focused 1.44 boot/reset/project-load/playback stress without overlap. Physical D/I-cache visibility remains a device-specific trial risk. The present observed clearing of cache/store-enable bits is useful evidence, not physical proof.

### 3. Choose and validate one installation and stock recovery route

Prefer the stock startup-menu route: physical MIDI IN, with the computer MIDI interface supplying MIDI OUT. Elektron's original-Digitone manual documents FUNC at power-on and the startup OS-upgrade option. Official support explicitly says the device USB port cannot be used for this route. A USB-connected computer MIDI interface can still supply its five-pin output; the synth connection is DIN.

Required result: identify the actual startup receiver/updater entry and its staged-buffer/checksum/program flow for the exact candidate, keeping bootloader/updater sections unchanged. The ordinary application receiver audit is not automatically evidence for this different route. Confirm the current physical OS, exact unit, backup state, available MIDI interface and stock-image recovery procedure before any experimental trial.

Acceptance: exact-image stock startup-path PC check where available, bounded erase/program footprint and source lifetime, plus a verified physical stock recovery/update baseline after backups. Successful stock recovery reduces uncertainty but does not guarantee recovery from every electrical/flash failure. Do not attempt a candidate transfer based only on the manual's route existing.

The stock flash loop's ignored tested error return remains relevant to update risk. Prefer a stock route without changing its flash driver; modifying flash-failure handling would be a separate project and would itself need review. Define an abort/recovery procedure appropriate to the selected route rather than claiming the receive freeze supplies rollback.

## Installation alternatives

| Approach | Scope impact | Decision |
|---|---|---|
| Normal application update over USB | Uses existing transfer path; current race/callback work would remain relevant to a custom persistent freeze. | Keep observations; pause further freeze implementation while evaluating startup DIN. |
| Normal application update over DIN | Avoids USB endpoint framing, but still uses the running application receiver and buffer. | Does not by itself remove the application buffer-use question. |
| Startup-menu update over DIN | Avoids the live application USB shutdown/restore lifecycle. Has an official stock recovery role. | Preferred route to investigate; exact startup internals/candidate acceptance remain unverified. |
| Elekloader packaging/core | Existing tool supports Digitone 1.44 and offers version-matched core/mod packaging. Could standardize startup, reservation and conflict checks. | Consider only if it demonstrably solves blocker 1 or 2. Porting now is extra integration work, not automatic safety. Its normal installation still uses stock updating. |
| Runtime RAM loading/debugger route | Might avoid persistent flash in some environments. | No accessible, tested route for this unit is established; do not base the plan on it. |

E03 already uses the size-efficient compressor and validated container checks. Elekloader is not needed merely to make this compressed file smaller. Its profile evidence does not independently certify exclusive RAM ownership or every recovery outcome. Neither route authorizes flashing E02.

## Hardware evidence belongs in a staged trial

Once the three work packages have explicit results, a trial can assess physical boot/cache execution, audio deadlines and musical behaviour. Begin with one simple track/sound, ordinary recording/playback, chromatic controls, a fixed nonchromatic arp and repeatable cold boots. Broaden to sustain, pattern replacement and heavier voices only after those observations pass.

Record matched settings and audio; stop on a hang, unexpected notes or repeatable discontinuities and use the verified stock recovery route. A clean recording cannot prove worst-case timing or RAM ownership. This is the outline of a later trial, not a claim all hardware unknowns must be solved on a PC beforehand.

## Next work and stop conditions

Follow-up: `Digitone-E03-startup-DIN-route-review.md` identifies and exercises the startup-menu dispatcher and exact E03 receive/program path in bounded, separate PC tests. The modeled menu enters its SRAM updater; exact E03 programming and three rejection controls pass. Full serial pacing and physical stock recovery remain pending. Development now returns to startup failure handling and the 1.44 reservation map; application USB freeze remains outside V1's critical path.

1. Validate the startup-menu DIN route for the current exact image and stock recovery prerequisites. If it genuinely avoids the application update lifecycle, retire USB freeze from V1's required implementation.
2. Resolve startup failure continuation and the 1.44 reservation map. Compare existing Elekloader mechanisms only if they can concretely replace an unresolved custom mechanism.
3. Rebuild one PC-only trial candidate only after code changes are defined, repeat focused integration/packaging checks, then present its exact changes and residual hardware risks for review.

No further USB callback/scheduler testing is on the critical path unless route validation shows it is needed. Do not expand into general USB updater hardening, whole-system exception certification or a Digiemu GUI repair project.

## Evidence and sources

Local reports: `Digitone-OS1.44-helper-contracts.md`, `Digitone-OS1.44-continuous-hooks.md`, `Digitone-OS1.44-audio-copy-audit.md`, `Digitone-E02-audio-isolation.md`, `Digitone-OS1.44E02-startup-memory-failure-review.md`, `Digitone-OS1.44E03-packaging-review.md`, `Digitone-OS1.44E03-queue-action-continuity-review.md`, and the E03 USB cancellation/ordering reviews. These are evidence summaries with explicit fixtures; this consolidation does not add execution coverage.

External sources checked 7 October 2026:

- [Elektron original Digitone manual, startup menu section](https://elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf), page 81 printed. Manual targets 1.41, so exact 1.44 implementation still needs verification.
- [Elektron startup-menu SysEx update guidance](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer).
- [Elekloader project and supported version-matched core](https://github.com/irpina/elekloader). Local reference pinned at `d1cdc74af61aaf6222b76f940e6b10bc5f586fed`; current upstream was consulted for the alternative, not silently substituted into tests.
- [Roland Rubix22 specifications](https://www.roland.com/uk/products/rubix22/), listing MIDI IN/OUT.

Firmware files are unchanged. E03 remains SHA-256 `8775320f161cb02efa8f51b2671034baf73eeec95f4bb66ffc20a29e9b0a2a3d`. No firmware was built or sent to hardware during this review.
