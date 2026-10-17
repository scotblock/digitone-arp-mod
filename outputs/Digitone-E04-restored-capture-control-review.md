# E04 restored-project capture and bypass control

9 October 2026. PC-only. E04 SYX, original emulator cards and the saved-mirror source fixture remain unchanged. No firmware was rebuilt or transmitted. The physical Digitone remains on working stock 1.44.

## Result

All four restored-project capture calls have matching register inputs and outputs, status flags and event bytes against the producer-bypass control. Each captures root 60 and enabled raw scale 0, writes the expected context word `800000bc` inside the private reservation, and resumes the original stock continuation. Complete isolated access traces contain no unexpected data address or unmapped access.

Unchanged E04 and the bypass control both restore the saved mirror during cold boot and clear the logo. The physical startup freeze remains unreproduced. These results close this specific capture check for the restored emulator project; they do not establish physical RAM ownership, cache visibility or interrupt timing.

## What was compared

Each startup starts from a fresh disposable copy of `PC_ONLY-saved-mirror-valid_first.img`. Its first mirror contains the retained serialized project from the user's stock emulator RAM session. The existing, unaltered header passed the actual stock validator in the preceding restoration investigation. This is a disclosed PC fixture, not a physical storage dump or an after-boot RAM resume.

Both runs observe a valid first header at `400a838c`, full mirror-read return at `400a83f4`, and publication of bank index 0 at `400a8410`. Neither enters default initialization at `400a8402`. Thus the enabled-scale restoration is executed in both controls.

The bypass uses the existing raw MAIN overlay restoring only stock bytes `254400082544003c` at `400947ec..400947f4`. The copier, initializer and all other hooks remain identical to E04. E04's SYX supplies the emulator's flash contents in both runs. The raw overlay is not a packaged firmware image.

Each reaches one actual intro exit and 138 main-loop entries. Each executes three native modeled DTIM1 interrupts, with zero host delay-semaphore kicks and zero general intro semaphore satisfactions. Only E04 enters producer_capture/capture/candidate_store/slot four times and resolve eight times; the bypass enters none of those helpers.

## Four actual calls

All four calls use A3/source `407fd414`, D4/track index 0, and A2/event `419f182c`. Source bytes are read at:

- Root `407fd7df`: `3c` (60).
- Scale `407fd7e2`: `00` (enabled raw scale 0).

The encoder stores valid bit + root 60 + scale index 1 (raw scale plus one), yielding `800000bc`. All four writes target candidate slot `47be1a24`. The bypass retains zeroes in the candidate slots.

| Call | Entry SP | Maximum local stack extension | Context write |
|---|---|---:|---|
| 1 | `41378550` | 92 bytes | `47be1a24 = 800000bc` |
| 2 | `40553c68` | 92 bytes | Same |
| 3 | `40553c88` | 92 bytes | Same |
| 4 | `40553c78` | 92 bytes | Same |

The original event writes remain A2+8 (`419f1834`) and A2+3c (`419f1868`), both with D4=0. All D0–D7, A0–A7 and SR agree between controls at each entry and continuation. SR is `2004` at both boundaries. The 72-byte event descriptors, private header and 64 bytes above entry SP also match at continuation. The difference is confined to the intended candidate-context word and temporary stack use below entry SP; the latter is balanced.

## Complete trace method and results

The continuous startup watches the stock hook site and continuation. For each call, an isolated ColdFire engine receives that exact captured CPU context plus code, source, event, private and stack pages copied from the running machine. All data-read/write and invalid-access hooks, and an instruction trace, are installed before execution. Unexpected pages are not automatically mapped.

Each isolated replay reaches `400947f4`. Its register results and observed event bytes, context slots, private header and caller stack bytes match the continuous execution. This is checked for both E04 and bypass, not assumed from a model-supplied branch choice.

The existing dynamically added continuous memory watcher may omit accesses already translated when the watcher is attached. Its partial `memory` lists remain diagnostic data; **the complete lists are `isolated_replay.memory`**. The short replays provide complete data accesses for the captured context, while the continuous runs establish that those calls occur during actual modeled restoration/startup.

Every E04 replay records 75 data accesses and 140 executed instruction-hook entries. Every bypass replay records the two original data writes and two instruction entries. The E04 access set is confined to:

- The two source bytes above.
- Private pointer/header checks and the two private state words checked before capture.
- One four-byte candidate-context write at `47be1a24`.
- The two original event writes.
- The caller stack, at most 92 bytes below entry SP.

No peripheral, DMA, other pattern or out-of-range context access occurs in these replay lists. The access and instruction counts show added work; they are not cycle estimates or hardware deadline measurements. The local stack extent excludes asynchronous interrupt frames and other task activity.

## Consequence

Both the earlier eight default-state calls and these four restored enabled-scale calls now have bounded successful capture controls. There is no observed register corruption, illegal data address or changed stock event output in these workloads. Removing capture does not expose a PC startup difference or reproduce the physical stall.

The remaining diagnosis should target differences the functional engine can hide. A focused next audit is instruction compatibility for the custom copier, fallback and producer paths actually executed before logo exit: the engine uses a ColdFire V4e core with capabilities beyond the MCF5441x, so passing execution alone does not establish every custom instruction's physical eligibility. That audit remains separate from physical cache, memory and interrupt timing validation. No new hardware trial is justified by this capture pass alone.

## Evidence

- `Digitone-E04-restored-capture-control-checks.json`: restoration markers, continuous runs, four input/output snapshots, instruction sequences and complete isolated accesses for each control.
- `Digitone-E04-restored-capture-control-summary.json`: passing bounds, encoding and cross-control comparisons.
- `work/test-E04-restored-capture-control.py`, `work/summarize-E04-restored-capture-control.py`.

The final paired run includes additional live/replay memory comparisons as well as the original register checks. All assertions pass. The source fixture's mirror payload still matches its recorded SHA-256; all original card hashes still match. E04 SYX SHA-256 remains `76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c`.
