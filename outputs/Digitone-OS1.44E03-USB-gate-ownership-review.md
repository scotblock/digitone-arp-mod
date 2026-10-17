# USB queues and receive-gate writers: PC-only audit

## Result

The primary USB-MIDI route respects the closed receive gate in the tested stock execution. Two concrete integration requirements were found: stock view entry can reopen the gate during a proposed freeze, and deferred USB work can remain pending after all MIDI queues appear empty. The freeze remains unimplemented in firmware. These checks do not establish hardware readiness or complete queue/alias ownership.

## Executed checks

- Primary USB bulk decoding (`4000499c`), registered callback (`400e8440`), chunk allocation, queue publication, input-task consumption and receiver dispatch executed. All 12,534 frames of the E03 stream reproduced the exact received payload and complete state in the unfrozen positive control. Completed bulk buffers and their release were fixtures; USB endpoint interrupts were not executed.
- Two complete USB frames queued before gate closure were consumed without changing receive state or buffer. A SysEx prefix started before closure, completed after closure, and was consumed without changing the receiver; its parser status returned to zero.
- Secondary cable callback (`400e8674`) published messages to its queue, but consumption did not reach the OS receiver in this fixture. This route remains unresolved; its absence of writes is not a freeze certificate.
- Stock deferred-work enqueue (`40001424`) and worker (`400012e4`) executed a queued USB decoder callback. All three MIDI queues were initially empty while deferred queue `4052815c` held one work item. Draining MIDI input alone left that item pending. Reopening the gate at that point allowed its two frames to change receive state and buffer. Executing deferred work, then consuming its frames while still frozen prevented the mutation.
- Stock update-view entry (`400c9210`) with the recovered enabled provider called gate-on and cleared the view busy flag at `+95`. Stock exit (`400c8e6e`) called gate-off. A host-only setter guard suppressed the entry's enable request and allowed disable requests; it is not installed in firmware. Unrelated sequencer calls were stubbed and natural transition eligibility was not established.

These are explicit PC interleavings. The deferred-queue counterexample proves the proposed input-only cleanup rule is insufficient in this model; it does not prove the device naturally schedules that sequence.

## Gate ownership

Gate `419950a4` is read at the receiver entry. Recovered literal references include initialization clear `400eb43c`, setter store `400eb530` in `400eb524`, and query `400eb538`. Gate-on wrapper `400ed8dc` and gate-off wrapper `400ed8ea` route through that setter. The recovered view entry and exit use those wrappers. Literal reference enumeration does not exclude computed pointers or bulk writes.

A one-time gate clear and the view busy flag cannot alone implement a persistent freeze: the executed entry callback can undo both. A separate ownership lease must prevent enable requests throughout the operation. Initialization/reset writes, stale cleanup, and unknown aliases still need lifetime coverage before selecting the guard's firmware implementation and storage.

## Required restoration contract

Keep the gate closed while deferred USB callbacks and resulting MIDI messages are processed, including frames already partly assembled. Queue-count zero at one instant is insufficient: new hardware completion or an executing producer could publish later. The next focused work is to establish producer-stop and in-flight completion conditions, resolve secondary-cable consumption, then extend the PC coordinator to enforce the guard and these conditions continuously through rejection and view transitions. Do not busy-drain a shared work queue inside its own worker; orchestration must permit the responsible tasks to finish.

Do not restore on unknown failure or after flash programming has started. The stock updater's ignored negative program return remains a separate unresolved failure-handling issue.

## Limits and reproducibility

No endpoint/DMA quiescence, physical cache coherence, actual exception cleanup, complete scheduler run, reserved-RAM ownership, or hardware flash failure behavior was certified. Existing heap, registry, display, transport, synchronization and flash fixtures continue to apply. No firmware bytes were edited or rebuilt and no device I/O occurred. Original 1.44, decoded stock MAIN, E02 and E03 hashes still match their recorded values.

Tests and results:

- `work/test-E03-USB-queue-freeze.py` / `outputs/Digitone-OS1.44E03-USB-queue-freeze-checks.json`: four bounded observations; secondary-route eligibility explicitly unresolved.
- `work/test-E03-USB-bulk-freeze.py` / `outputs/Digitone-OS1.44E03-USB-bulk-freeze-checks.json`: three passing checks, including full-stream control.
- `work/test-E03-deferred-USB-freeze.py` / `outputs/Digitone-OS1.44E03-deferred-USB-freeze-checks.json`: two passing controls contrasting frozen drain with premature reopen.
- `work/test-E03-gate-writers.py` / `outputs/Digitone-OS1.44E03-gate-writer-audit-checks.json`: five passing writer/host-guard checks.

This report extends the earlier receive-freeze design review; its DIN-only USB coverage limitation is superseded for the primary software route, but not for hardware completion or the alternate route.
