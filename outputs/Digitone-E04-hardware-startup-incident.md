# E04 physical startup failure and stock recovery

Date: 8 October 2026. Original Digitone, user-reported stock OS 1.44 baseline, Rubix22 startup-menu DIN update route.

## Observed result

The user reported E04's upgrade completed, but normal startup remained on the Elektron logo. The screen showed an H at bottom left and 1.44 at bottom right; the logo did not dissolve as it does with stock. The meaning of H and the exact stalled instruction are unestablished. Version 1.44 alone cannot distinguish E04 from stock.

After instructions to use the existing startup-menu recovery route without either reset option, the user reported: "the stock firmware is reinstalled and working". The current physical device is therefore user-reported restored to working stock 1.44. No agent tool transmitted either firmware image.

## Image identity

E04 file provided for the trial: `Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx`.
Verified pre-trial SHA-256: `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`.

Stock recovery copy: `stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx`.
Verified pre-trial SHA-256: `d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.

## Consequences

The physical trial failed its first startup acceptance criterion. Existing PC loader/startup passes do not predict the observed device behavior adequately. Successful stock recovery establishes recovery for this incident only; it does not prove all future failures recoverable.

Do not reinstall E04 or promote it to hardware-ready. The image remains unchanged for diagnosis. No physical scale, sustain, queued-note or timing test was reached.

No cause is established: cache visibility, RAM placement, startup state or initialization/hook control flow remain hypotheses. A displayed logo does not prove a specific initializer or helper executed, and a completed transfer report is not a physical flash readback.

## Next bounded investigation

Tenth follow-up completed on 9 October: `Digitone-E04-PC-instruction-correction-review.md` corrects all five unsupported stores in separate raw overlays. Copier grows 16 bytes within padding and preserves all continuation registers/SR; ready replacement keeps its ten-byte extent. Strict static checks, 33 fallback contract cases and four cold/intro controls pass, including default/restored projects and pre/post-initializer metadata failures. Original E04 and saved files remain unchanged. Next test corrected overlay with loader-derived state and playback; no hardware retry is authorized by these PC results.

Ninth follow-up completed on 9 October: `Digitone-E04-startup-instruction-compatibility-review.md` finds five documented unsupported immediate-to-absolute MOVE.L stores: four copier header writes beginning `4029c4e0` and fallback ready write `47be0998`. The emulator and local decoder accepted these operand combinations. A strict documented-rule guard stops the actual copier at its first bad store after copying but before header setup. This is a concrete defect and plausible cause, not a physical fault-PC diagnosis. Next correct all five with preserved-state PC overlays and repeat strict/default/restored startup tests. E04 remains unchanged and must not be retried on hardware.

Eighth follow-up completed on 9 October: `Digitone-E04-restored-capture-control-review.md` compares E04 with the producer-bypass overlay after native cold restoration of the enabled-scale mirror. All four captures have identical register/status/event results against bypass; exact-state replays record 75 bounded data accesses per helper invocation and the intended `800000bc` context write. Both controls reach the UI. No physical failure reproduction. Next audit physical instruction eligibility in custom pre-logo paths, separately from unresolved hardware cache/timing. E04 and original cards remain unchanged.

Seventh follow-up completed on 9 October: `Digitone-E04-restore-versus-replace-review.md` traces two mirror-header checks, SPI fallback and default selection. Disposable fixtures use a retained emulator RAM mirror whose unaltered header passes stock validation. Stock/E04 both cold-restore its enabled-scale pattern; E04 also rejects a bad first checksum and restores from the second bank. The earlier `0fc00000` label is corrected to special project index 128. Four restored-state captures now replace the eight default-state calls in this workload. Physical failure remains unreproduced; next inspect those four calls with complete access tracing/bypass. E04 and original cards remain unchanged.

Sixth follow-up completed: `Digitone-E04-source-initialization-and-saved-project-review.md` traces root/scale conversion before all eight early captures and the active-pointer argument chain. Stock/E04 cold boots with factory/saved emulator card copies all pass, but none restores the enabled-scale saved RAM pattern. A separate origin run observes 39 working-project writes before its first read; modeled flash settings are blank. These passes do not certify the physical saved-project path. Next trace restoration versus replacement preconditions. Original cards and E04 remain unchanged; no hardware reinstallation.

Fifth follow-up completed: `Digitone-E04-producer-startup-control-review.md` compares unchanged E04 with a raw PC overlay restoring only the eight producer-site bytes. Both clear the logo; all eight input/output register sets match. Exact-state isolated replays capture all data accesses: valid source bytes, private checks, one bounded candidate write, original event writes and 92 bytes of local stack use. No unexpected access or physical failure reproduction. Next investigate source initialization and saved-project startup differences; E04 SYX remains unchanged and no hardware reinstallation is proposed.

Fourth follow-up completed: `Digitone-E04-DDR-and-pre-logo-hook-review.md` derives a 128 MiB window from stock DDR settings; the reservation fits that configuration. A new native-delay E04 run observes eight producer-capture calls before logo exit, with context ready; pitch/allocation/copy hooks are not entered in that workload. The capacity check does not prove physical RAM ownership. Next isolate those early producer calls and audit their startup input objects and dereferences. No hardware reinstallation.

Third follow-up completed: `Digitone-E04-startup-components-and-cache-review.md` records successful copier-only, host-seeded initializer-only and combined PC controls under loader-derived cache settings. The traced section-2 bootstrap disables data cache before copying; a separate hypothetical copyback model shows why that prerequisite matters but does not diagnose the physical fault. The stall remains unreproduced. Next verify DDR/address-decoding assumptions for the reservation and attribute runtime hooks actually entered before logo exit.

Second follow-up completed: `Digitone-E04-startup-completion-producer-review.md` identifies the early signal as a one-shot DTIM1 delay. Matched stock/E04 runs now execute three native timer interrupts and semaphore wakes with zero host completion kicks, and both reach the UI. The modeled copier runs before those waits; no direct memory overlap or permanent interrupt-mask leak is observed. Physical failure remains unexplained. Next separate copier and initializer effects in PC controls and review inherited cache/memory attributes; no hardware reinstallation.

Follow-up completed on 8 October 2026: `Digitone-E04-logo-startup-comparison-review.md` records matched stock/E04 cold and intro runs. Both clear the logo with general semaphore unblocking disabled; removing the earlier hardware-completion stand-in stops both before initialization. E04's modeled initializer is ready before intro exit. The physical E04-only stall remains unreproduced and unexplained. Next trace the actual early completion producer and assess interactions with the changed startup copy/cache path; do not reinstall E04.

Eleventh follow-up completed on 9 October: `Digitone-E04-PC-loader-playback-review.md` carries the corrected raw overlay from the saved actual E04 loader handoff into default/restored startup and snapshot-linked playback. Both reach the UI without host completion kicks. Default enabled-scale playback executes 43 quantizer calls with 33 expected note changes; all capture/oracle checks match. Restored startup and captured context pass, but its controlled sequence never enters the quantizer, so restored arp behavior remains unverified. All collected PCM buffers are zero-filled: their equality does not validate audible playback. Original E04/stock firmware remain unchanged; no corrected packaged loader test or hardware reinstallation. Next establish an eligible restored-state arp workload and a working modeled DSP/audio path; then verify a separately named corrected PC-only package through the actual loader. Physical cache/timing and RAM ownership remain unresolved.

Twelfth follow-up completed on 9 October: `Digitone-E04-PC-restored-arp-audio-review.md` identifies missing section 7 in the new test folders as the cause of the handshake-only, silent DSP model. Fresh folders now include the unchanged stock DSP program, and playback waits for guest DSP boot/renders. Native panel actions enable the restored T1 sound's arp and create a sequencer trig. The sequence-only controls execute seven valid-context quantizer calls; all seven enabled-scale notes change 60 to 59 as expected. Nonzero PCM is produced, with no DSP error, halt or strict instruction violation. Ordinary pitch streams match stock-site controls, though their audio bytes differ and that cause remains unproven. A separate mixed-input test exposes 26 zero-context live-note quantizer calls out of 27; only its sequencer note changes. Next trace the first live note's context capture/copy/read guards against the successful sequencer control. E04 and stock firmware remain unchanged. The physical freeze, cache/timing, RAM ownership and corrected packaged-loader path remain unresolved; no hardware reinstallation.

Thirteenth follow-up completed on 9 October: `Digitone-E04-PC-live-context-loss-review.md` follows the selected live E64 event from allocator return `400ff504`, through raw 72-byte copy `400ff5f6` and immediate publication `40100252`, into selection and pitch. This stock creator (`400ff3ec`) bypasses the existing capture/copy hooks. Its candidate slot is only cleared, and snapshot returns zero before commit. Commit correctly replaces the sequencer frame with identity 2/word 0/cookie 0; the subsequent read rejects the absent cookie at `47be0106`. The sequencer control retains `800000be` and changes 60 to 59. All 22 evidence checks pass, and the full 27-call signature matches the previous uninstrumented workload. Next establish receiving-pattern ownership and the capture point for this live creator, including its two alternate copy branches and failure/release paths, before a PC-only fix. Firmware remains unchanged; no new helper bytes or hardware transmission.

Compare the complete stock and E04 startup path around logo/intro completion using matched initial state. Identify what the packaged PC tests accelerate, fixture or skip before their settled-interface result, and test those boundaries without assuming the device's startup state matches the prepared emulator drive. Preserve both exact images. Any corrective candidate must be tested on the PC and reviewed before another hardware trial; do not introduce unrelated USB updater changes.

Fourteenth follow-up completed on 9 October: `Digitone-E04-PC-live-capture-review.md` establishes the stock receiving-pattern index/base chain and tests a separate 474-byte PC capture/bind/copy overlay with 2080 bytes of additional state. Three guest note-on captures agree with pattern 1 then pattern 2 ownership; an actual pointer publication precedes old-context E/G playback, and fresh F uses the new context. All 53 quantizer calls have valid context and match the pitch oracle; seven contract groups and 22 summary checks pass. New state is initialized by the host installer only; startup/reset copying, copy-source serialization, alternate-selector execution and physical RAM/cache/timing remain unverified. Original firmware and payload hashes remain unchanged; no new SYX or hardware retry.

Fifteenth follow-up completed on 9 October: `Digitone-E04-PC-live-storage-startup-review.md` connects added live-context code/storage to a separate raw PC startup candidate and guarded stock-initializer reset. 33 reset/failure cases, repeated poison/reset, four loader-derived cold/intro controls and startup-derived playback pass. The larger padded raw source is overlaid after the original loader handoff, not loaded from a new packaged container. No poststartup code or sidecar seed is required. Source/copy interleavings, native UI reset coverage and physical RAM/cache/timing remain unproven; original firmware is unchanged.

Sixteenth follow-up completed on 9 October: `Digitone-E04-PC-reset-overlap-review.md` reproduces two conditional overlap hazards and tests a separate interrupt-masked 72-byte copy/context guard. Fifteen stock-equivalence controls, two loader-derived starts and 53 playback pitch checks pass. Controlled test-exit setup preserves queued input and pending context before reset; actual earlier command/callback shutdown remains unverified. Full pool reset can invalidate a held event in the injected controls, a stock lifecycle issue not proof of a normal reachable failure. Firmware remains unchanged; physical RAM/cache/timing and hardware readiness remain unproven.

Seventeenth follow-up completed on 9 October: `Digitone-E04-PC-diagnostic-exit-review.md` executes 1.44 diagnostic entry, post-dequeue native note creation, parsed EXIT_TEST_MODE comparison and both preparation branches through actual pool reinitialization. Two guest-produced queued notes survive to reset and are returned to the free pool by reconstruction. Native page removal/mutex/callback controls likewise preserve input and owners before reset. Nine execution controls and 16 summary checks pass; no local shutdown barrier is supplied by these tested paths. Transport admission, real page-selection state, concurrency and physical RAM/cache/timing remain unproven. Firmware and current raw candidate are unchanged.

Eighteenth follow-up completed on 9 October: `Digitone-E04-PC-reinitialization-protection-policy.md` defines V1 as one initialization per fresh boot with no live pool reconstruction. Whole-operation rejection must precede command flags or page/handler changes. PC policy assertions and native state controls pass; injected initializer-only zero return is ignored by the actual setup caller. This is a specification/admission model, not an installed native guard. Command cleanup/return continuation, UI entry/close veto and persistent latch integration remain required. Original images and current guarded raw candidate remain unchanged.


## Nineteenth follow-up: local rejection continuations

The tested stock continuations can reject matched diagnostic commands and selected page-manager operations without entering pool reconstruction. Nine bounded native PC controls pass. The host supplies the admission decision, message pointer or predicate result; no native guard or boot latch has been installed. Original firmware containers, E04 files and the current raw PC candidate are unchanged (hash checked).


See `Digitone-E04-PC-rejection-continuations-review.md`. Outer selection/direct removal coverage and pending-close handling remain unresolved; no native guard installed.


## Twentieth follow-up: direct-removal bypass callers

Ten native PC controls pass. Sole recovered directed-removal caller aborts "UI Test View", with native name-lookup controls skipping "AudioTestMenuView". Locked refusal balances strong reference and mutex cleanup but the caller still clears the separate UI-test flag. Unreferenced front remover executes without an exit callback in constructed heap-backed controls; computed callers remain unproven. No guard installed, original and raw candidate hashes unchanged. See `Digitone-E04-PC-removal-bypass-review.md`.


## Twenty-first follow-up: audio-test selection trace

Stock 1.44 constructs AudioTestMenuView at settings +2b4, but none of the eleven recovered settings callbacks reads/selects it. Fifteen native PC controls pass. Manager-only denial leaves parent selection changed; a host-selected earlier refusal before the shared-helper assignment preserves it. Actual application selector remains unidentified. No guard installed and firmware/raw candidate hashes unchanged. See `Digitone-E04-PC-audio-selection-review.md`.


## Twenty-second follow-up: retained-child restore bypass

Native parent close saves selected child at +8c; closure clears +84; re-entry restores +8c and calls manager directly, bypassing shared helper. Four bounded PC controls pass. Manager refusal consumes retained reference and leaves selected restored; local earlier defer preserves both but follows parent entry callbacks. Full-entry probe stops in incomplete synthetic renderer at 400e4fcc, not evidence of a firmware fault. Initial audio selection remains unidentified. No guard installed, firmware/raw candidate hashes unchanged. See `Digitone-E04-PC-computed-selection-review.md`.


## Twenty-third follow-up: real audio constructor and complete restore

Two native PC controls complete restoration through rendering and real audio entry using the full stock constructor and settings-style ownership wrapper. Saved reference is produced by native parent close; registered clear target executes directly; full diagnostic exit list remains unexecuted. Audio vector changes to 400e7b32 while queued notes/pool/context remain preserved. Shared helper is bypassed. Initial selection/outer parent state constructed; original selection request, whole-parent admission and hardware validation remain unproven. No guard installed; firmware/raw candidate hashes unchanged. See `Digitone-E04-PC-stock-audio-restoration-review.md`.


## Twenty-fourth follow-up: parent callbacks and restore refusal

Four PC controls pass with stock audio child and real settings base-parent construction prefix. Entry callback 400e47ae registers parent in active-page vector; refusal before callbacks preserves it, refusal after callbacks leaves registry mutation while preserving retained child. Full settings constructor hits a missing initialized application dependency at 400634ec; separately recorded as fixture gap. Outer parent publication/void callback contract remains unverified. Native guard uninstalled and firmware/raw candidate unchanged. See `Digitone-E04-PC-real-parent-restore-refusal-review.md`.


## Twenty-fifth follow-up: outer publication and local guard contract

Ten PC controls execute manager and actual application wrapper. Manager publishes parent before entry and ignores entry return. Early entry tail leaves published/unbound parent with success; after-callback child defer preserves completed parent and pending child, with balanced cleanup. Chosen local policy: complete normal parent entry then defer retained AudioTestMenuView before transfer. No native guard installed; full-settings dependency, higher callers/admission/lifetime/hardware checks remain. Firmware/raw candidate hashes unchanged. See `Digitone-E04-PC-outer-parent-publication-review.md`.


## Twenty-sixth follow-up: disposable native UI guards

150-byte separate PC overlay tested: retained audio defer after parent entry and explicit audio refusal before assignment. Sixteen controls and eight CPU/state stock-parity comparisons pass, plus ISA_C/MOVE checks. Compiled live constants are test controls; no persistent admission, certified placement or startup integration. Existing firmware/raw candidate unchanged. Close/re-entry and native latch remain. See `Digitone-E04-PC-ui-defer-overlay-review.md`.


## Twenty-seventh follow-up: deferred close/re-entry and final release

Two native PC lifetime runs pass: three enter/defer/close/remove cycles each, plus final parent/audio owner release. Real parent exit callback dispatch balances registry and selected-owner cleanup; retained audio stays at two owners across cycles, drops to one on parent destruction, then frees on final handle release. No audio diagnostic entry/exit or pool reset reached; note/pool/context preserved. Original snapshot task identity used to respect inherited mutex ownership. Persistent admission, full parent construction, concurrency and hardware validation remain. Existing firmware/raw candidate/guard blob unchanged. See `Digitone-E04-PC-deferred-page-lifecycle-review.md`.


## Twenty-eighth follow-up: persistent admission candidate

Separate native PC overlay replaces compiled live controls with persistent state reads. Thirty state/ABI controls, twenty actual reset/failure controls, thirty-six UI-route controls and six native lifecycle cycles pass. Candidate 47be2840 is preserved by observed warm resets/UI destruction but overwritten with zero by the early copier; zero denies and never rearms COLD. Trusted post-copy cold seeding, startup completion provenance, native initializer/whole-command admission and physical ownership remain unimplemented/unproven. Existing firmware/raw candidate/old UI blob hashes unchanged. See `Digitone-E04-PC-persistent-admission-review.md`.


## Twenty-ninth follow-up: post-copy cold boundary

Default/restored loader-derived traces preserve a fixture marker from copier tail 4029c518 to initializer. Tail IPL is 5, requiring explicit mask protection. Preferred consumption boundary is startup call 4008d318 before setup flag mutation; boot flags bit 40 instead selects diagnostic 4008d326 and must invalidate the permit. Three native helper/wrapper controls and two stock branch controls pass. No native startup seed/guard integrated; computed replay, full completion/failure continuation and physical ownership remain unproven. Existing artifact hashes unchanged. See `Digitone-E04-PC-cold-permit-boundary-review.md`.


## Thirtieth follow-up: native cold seed/claim experiment

Host-loaded 280-byte native overlay seeds COLD after copier and claims INITIALIZING before normal setup flags in both default/restored loader-derived PC startup runs. Six seed, five refusal and one actual diagnostic-branch controls pass. Refusal uses a proposed interrupt-masked core stop, not a verified graceful/hardware failure path. Forged copier replay recreates a permit, demonstrating provenance checks are insufficient by themselves; reachable stock warm replay is not established. Completion-to-LIVE, producer gates, shared initializer/command guards and packaged code delivery remain unintegrated. Firmware/raw/previous overlay hashes unchanged. See `Digitone-E04-PC-native-cold-admission-review.md`.


## Thirty-first follow-up: startup completion versus input activation

Four startup runs, fourteen handler probes, six DIN interrupt probes and two settled input sessions pass. Stock config opens note gate before initializer; direct handler can reach producer before initialization and cached publication precedes the later live producer. Early DIN IRQ drains bytes without observed note production, but settled restored DIN input publishes while phase remains INITIALIZING. Late normal completion candidate is 4008d3fa after final startup call; LIVE/input-phase guards remain unimplemented. No universal transport/IRQ exclusion or hardware readiness claim. Existing firmware/raw/old UI blob hashes unchanged. See `Digitone-E04-PC-startup-producer-order-review.md`.


## Thirty-second follow-up: guarded input and native LIVE publication

Separate 492-byte host-loaded overlay guards packet, cached selector and live-producer entry, then publishes LIVE after full final startup call with observed normal conditions. Eighteen denials, four stock-parity pairs, nine completion controls, three native cold startups (including context-disabled fallback), three settled MIDI sessions, an IRQ publication control and a controlled receiver phase handoff pass. Native stores zero/COLD/INITIALIZING/LIVE join in startup; optional failure retains stock input. All-route and warm reset/command admission, packaged code delivery and physical provenance/storage/cache/timing remain unresolved. Firmware/raw/older overlay hashes unchanged. See `Digitone-E04-PC-input-live-review.md`.
