# Input/reset overlap audit and guarded PC copy candidate

One concrete copy gap has a tested PC guard. Full pool-reset exclusion remains unproven, and these results do not make a hardware update ready. No firmware container or physical device is changed.

## Boundary controls and their limits

Five controls execute the actual machine-code helpers and complete stock initializer with explicit pause/reset/resume or descriptor-rewrite injection. The reset uses a separate stack, and interrupted CPU registers/status/stack are restored before resuming. These are adversarial controls, not evidence that the real dispatcher permits each injected interleaving.

1. Reset before or immediately after the byte copy clears the captured scale. More seriously, the allocated event is again the stock free-list head: publication would use an address whose allocation lifetime has ended. This is a stock pool-reconstruction hazard as well as a mod lifetime concern. The ready flag does not supply producer shutdown or stop a stock event publication.
2. A pending note-on snapshot cannot reappear across the clear merely because its stack input address is reused. Its subsequent bind receives zero and passes through safely.
3. With the real reset paused before its stock continuation and ready zero, a note-on capture refuses metadata access. Its displaced stock input-record writes still happen; the gate protects metadata, not all input processing.
4. Rewriting a source descriptor/context after its bytes have been copied can make the original wrapper combine old bytes with a new scale. The original observed live copy runs at SR `2000` (interrupt mask zero), so an outer interrupt mask cannot be assumed. Actual producer admission/reentry during that exact interval is not established by the injected control.

## Narrow PC copy guard

A separate 182-byte helper at `47be3600` masks interrupts across the stock 72-byte memcpy and its metadata transfer. It preserves the incoming interrupt/status-control bits and the stock copy's resulting condition flags and register values. Both direct and indirect live-copy targets now point to it in a separate raw startup candidate.

Fifteen controls across five source/destination/readiness/length cases and three incoming statuses match stock copied bytes, all returned registers, stack and full status. A level-six rewrite request at the old race boundary observes mask seven and is deferred by the test's interrupt-admission check; after return, updating the source context leaves the allocated event's old snapshot unchanged. This is a mask-semantics control, not execution of a full queued interrupt dispatcher or proof against DMA/nonmaskable writes.

The guarded raw candidate is copied by guest startup and tested through two loader-derived cold/intro runs (default and restored project). A startup-derived playback session needs no extra code/storage seed. All 53 pitch checks match with valid context; old notes keep their scale after actual pattern publication, fresh notes use the new scale, MIDI delivery completes, and actual DSP playback continues without an emulated halt/error. Earlier reset-failure controls remain evidence for the unchanged reset routine; they were not all repeated for this candidate, which changes only the copy target, appended code and copier count.

The padded raw resident image is 14,008 bytes. It is not a final packed firmware layout or an updated loader/container test. Original E04/stock update and original MAIN/payload hashes are preserved. Previous raw candidates remain available unchanged.

## Reinitialization route audit on 1.44

The sole recovered literal direct initializer call is `4009c5a4`, in wrapper `4009c5a0`. It has two recovered relative callers: `4009c5d4` (setup) and `4009c6d4` (synthetic queue construction). No literal or recognized relative reference to diagnostic entry `4009c6d0` is found; this does not exclude a computed caller.

Setup `4009c5ae` is reached through branches from normal helper `4009d0d8` and test-exit helper `4009d0ea`. The command comparison at `4008b87a` uses the actual string `#EXIT_TEST_MODE` at `401df5fa`, then calls `4009d0ea` at `4008b890`. Callback thunk `400b25c2` also tail-jumps there; its address is loaded at `400b2c48`, stored in the callback record and passed to `400e57d4`. This proves a registered address escape, not execution of its dispatch/shutdown preconditions.

The controlled execution starts directly at `4009d0ea` with an actually published stock event, MIDI receive mask 3 and existing pending/descriptor context. It selects the setup branch with preparation bit `80000` clear in `402296f0`; that branch skips conditional preparatory routines and reaches the initializer with the same queue, receive gate and pending context, at mask zero. This rejects the local setup branch as a complete barrier under those controlled entry conditions. It does not prove the command/callback dispatcher can reach it with those owners in a real device state. The branch with preparation bit set and its transitive shutdown effects remains outside this execution.

## Hardware readiness and next bounded check

Ordinary pattern handoffs are observed and preserve context; the full pool reset is a different operation. The readiness flag and narrow copy guard cannot exclude a reset between event allocation and publication. The concrete next target is the 1.44 test-exit command/callback admission and conditional preparation path: establish whether it stops producers and drains/retires retained owners before setup. Do not replace this question with more general USB updater work or claim every stock lifecycle hazard is caused by the mod.

Physical ownership of the reserved RAM, physical code-cache visibility, the duration of the added interrupt-masked copy and real startup behavior remain unvalidated. Passing an assumed-cost PC timing model cannot certify them. Full exception cleanup, native UI reset, alternate-selector execution and allocation exhaustion also remain outside this bounded result. No hardware retry or new flashable image is implied.

16 summary checks pass. Evidence: `Digitone-E04-PC-input-reset-overlap.json`, `Digitone-E04-PC-test-exit-reset-entry.json`, `Digitone-E04-PC-atomic-live-copy.json`, `Digitone-E04-PC-atomic-storage-startup.json`, `Digitone-E04-PC-atomic-storage-playback.json` and `Digitone-E04-PC-reset-overlap-summary.json`. Stock caller disassembly: `work/PC-live-reset-callers-disassembly.txt`. Separate raw candidate: `work/os144/PC_ONLY-atomic-storage-*`.
