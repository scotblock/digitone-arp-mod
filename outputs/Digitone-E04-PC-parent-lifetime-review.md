# Digitone 1.44: source-parent lifetime and reset refusal review

PC-only audit. Firmware containers and existing overlay binaries remain unchanged. This is not a hardware-trial approval.

## Concrete findings

The retained pattern callback needs both its destination buffer and its source owner to remain valid. Four paired stopped-state controls verified this: the live owner supplies the normal getter and conversion; child teardown, parent teardown and deleting-parent teardown change the child's virtual table to `40195abc`. The callback at `4002c1e4` then selects `fffffdf8` as its getter. The tests stop before dispatch to that invalid address. The fixed destination remains unchanged. These destructive calls were explicitly forced; they are not evidence that normal stock operation permits the interleaving.

The parent has global shared ownership: raw pointer `419f0de0`, control pointer `419f0de4` (observed control `41a0a750`). The restored state has strong=1, weak=1. A separate 64-bit resource lifetime counter at `419f0d70:419f0d74` equals 94. Literal scans recovered 94 increment sequences and 94 conditional decrement sequences. The increments lie after 94 distinct entries in the stock 133-entry startup table at `4028e63c`, consumed by the loop around `4008d0a4`. This strongly supports a startup/global-resource lifetime mechanism rather than a per-note lease. The nearest-constructor and adjacent-finalizer mapping remains structural evidence, not a complete call-graph certificate.

One continuous restored-state test ran the stock descriptor builder, publisher, clone, consumer, conversion and both descriptor cleanup paths. Counter=94, parent pointer, control pointer, strong/weak counts and owner virtual table remained constant. No watched counter writes, global-parent release or parent/child teardown occurred. The raw descriptor does not acquire a per-callback owner reference in this observed lifecycle. The existing global owner protected the parent throughout the tested interval; arbitrary shutdown was not exercised.

Three native counter controls clarified the boundary. Calling initializer `4014d9e4` increments 94 to 95, and its finalizer `4001c92a` returns it to 94 without releasing the parent. A nonlast finalizer changes 94 to 93 without parent release. With an explicitly supplied counter=1 fixture, the same finalizer changes it to zero, releases `419f0de4`, executes parent deletion and changes the child virtual table. Thus the source owner can be deleted at the lifetime boundary; zero is not just an unused condition. This forced fixture does not establish how real shutdown reaches zero or whether workers have already stopped.

The diagnostic caller `4009c6d0` is a distinct refusal issue. In a stopped LIVE-state test its call to guarded wrapper `4009c5a0` returns without entering the storage initializer, but the caller continues: it allocates a type-5 event and publishes it via `40100178`. The test stops immediately after this first publication, before the drain loop. The custom queue and monitored pattern owner remain unchanged. Inner refusal therefore cannot be treated as refusal of the whole command. The normal admission path to this diagnostic caller remains unrecovered.

## What this closes and what remains

Nine bounded controls passed: four owner/dispatch controls, one diagnostic continuation, one continuous queue lifecycle and three counter controls. They establish the failure mechanism and show that the parent stays retained in the actual tested playback interval. The earlier raw-pointer observation alone was insufficient to infer ordinary playback permits parent destruction.

The next bounded audit is application-wide shutdown/finalization admission and worker retirement at the counter's final-release boundary, plus the actual caller/admission of `4009c6d0`. No new binary guard is justified yet from a stopped synthetic call alone. If live admission is established for that command, refusal must cover its outer entry before event publication, with its callers' return handling verified.

Global computed writes and every reset caller remain uncertified. Physical DMA, cache coherence, hardware timing and the cause of the earlier hardware startup hang are not validated by these tests. E04 is not hardware-ready.

## Evidence

- [Digitone-E04-PC-parent-destruction-retained-callback.json](./outputs/Digitone-E04-PC-parent-destruction-retained-callback.json)
- [Digitone-E04-PC-diagnostic-reset-refusal-continuation.json](./outputs/Digitone-E04-PC-diagnostic-reset-refusal-continuation.json)
- [Digitone-E04-PC-queued-pattern-parent-lifetime.json](./outputs/Digitone-E04-PC-queued-pattern-parent-lifetime.json)
- [Digitone-E04-PC-parent-counter-finalization.json](./outputs/Digitone-E04-PC-parent-counter-finalization.json)
- [Digitone-E04-PC-parent-counter-lifetime-static.json](./outputs/Digitone-E04-PC-parent-counter-lifetime-static.json)
- [Digitone-E04-PC-parent-global-holder-callers.json](./outputs/Digitone-E04-PC-parent-global-holder-callers.json)
