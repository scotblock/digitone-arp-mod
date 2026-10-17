# PC-only receive-freeze design

## Result

Nine transaction cases and six isolated acquire cases pass. The proposed freeze prevents the observed buffer mutation in the tested DIN path, including frames queued before acquisition and a partial SysEx frame begun before acquisition. No firmware file was edited/rebuilt and no device transfer occurred. This is a prototype design, not an installed firmware hook or complete release certification.

## Transaction contract

The coordinator owns a single update-view token and records the prior gate state. A second acquisition and cleanup by another token are rejected. Acquire must run at a point where no receive writer is still executing: mask CPU interrupts, snapshot gate `419950a4`, call stock setter `400eb524(0)`, then restore the caller interrupt level. Only after that does the stock action obtain and validate the completed buffer.

Queued DIN frames are consumed while the gate is closed through the actual byte parser, input queue, DIN consumer, SysEx routing and receiver. The receiver checks the current gate, so those messages do not mutate its buffer/state. The gate remains closed across validation, simulated erasure/programming and the success/reset boundary.

A known pre-write rejection can restore exactly the saved gate state only while the same view/token owns the operation, no flash operation has begun, queued input has been drained while frozen, and no partial SysEx frame remains. A partial frame keeps the gate closed; the test supplies its tail, drains its resulting message while frozen, then permits restoration. The prototype does not indiscriminately reset the whole MIDI parser. Subsequent new start input is accepted after a permitted gate restoration.

An already-disabled gate remains disabled. A changed view does not allow stale cleanup to reopen reception. Unknown exceptions latch a fault and keep the gate closed. After any modeled erase/program operation starts, cleanup cannot reopen reception; hardware recovery is a separate requirement.

Coordinator ownership/fault state is stored on the PC host for these tests. No Digitone RAM owner/token storage has been selected or certified.

## Tested cases

| Case | Result |
|---|---|
| Valid image, complete frames already queued before freeze | Queue drains without receive-buffer changes; exact advertised image is programmed in simulated flash; gate remains closed. |
| Valid image, SysEx prefix begun before freeze | Tail finishes while frozen; resulting frame is ignored by receiver; exact image programmed; gate remains closed. |
| Whole-image checksum rejection | Stock action returns 3 before flash. Queued input drains while frozen; saved enabled gate restored; new reception can start. |
| No completed image | Action returns 2 with no flash; prior gate restored. This explicitly invoked action is a failure fixture, not a claim that incomplete reception publishes a work item. |
| Prior gate disabled | Rejection restores zero, without enabling reception. |
| View ownership changed | Rejection leaves gate closed; stale restoration is blocked by modeled ownership state. |
| Partial frame on rejection | Restoration delayed until tail/message consumed while frozen; new reception then works. |
| Unexpected exception | Modeled coordinator exception latches fault; gate remains closed. Actual CPU exception unwind/cleanup is not tested. |
| Negative page-program return | Stock updater continues despite the injected negative return; the freeze stays closed after flash start. This exposes an unresolved abort-handling requirement. |

The flash-error test changes the simulated operation's return value after the existing simulator has copied bytes; it is a return-handling test, not a simulation of a physical flash's partial write, timeout or power loss. It verifies that the stock loop proceeds to later pages and programming-complete despite that negative result. A receive freeze alone does not fix this.

## Atomic acquire test

A 36-byte diagnostic instruction sequence executes only in scratch PC memory. It preserves D2/D3, saves SR, masks interrupts, reads the old gate, calls the existing setter with zero, returns the saved gate and restores the incoming interrupt level. Tests cover prior gate 0/1 with incoming interrupt levels 0, 3 and 7. All preserve the tested registers and caller interrupt level, and close the gate before returning. This code is not placed in a firmware image or certified owned executable space. The transaction tests use the host coordinator and stock setter; they are not a continuous execution of this scratch sequence installed as a hook.

## Remaining gaps before firmware integration

- Prove acquisition quiescence: interrupt masking does not stop DMA or a producer that had already passed the gate. The single-core task-order evidence helps, but complete producer/alias coverage remains unproven.
- Cover USB and every input queue/partial-framing path. Current queue draining and partial-frame restoration evidence is DIN only. Reopening must remain disallowed when any producer's cleanup is unproven.
- Prevent another mode/view gate writer from reopening reception during the lease. Model ownership checks do not yet enforce the actual application gate-writer lifecycle.
- Find owned storage/executable placement for the transaction metadata and hook, and account for startup/reset lifetime. The host token is not a firmware allocation.
- Implement and test explicit handling of flash error returns and unknown faults. The present stock loop ignores the tested negative return; there is no demonstrated safe hardware abort/rollback.
- Audit the other compatibility/rejection results and real exception exits. Only stock returns 2/3 and a modeled exception policy are covered here.
- Validate real kernel scheduling, transport pacing, cache coherence, flash failure/reset behavior and timing. The earlier registry/heap/display/project-save/lock/thread/flash fixtures still apply.

The next integration audit should first close USB/queued-producer coverage and actual gate-writer ownership, before implementing the freeze in firmware. Startup failure handling and reserved-RAM ownership remain unresolved independently. Still not hardware-ready.

## Reproduce

- `work/test-E03-receive-freeze-design.py`
- `work/test-E03-freeze-atomic-acquire.py`
- `outputs/Digitone-OS1.44E03-receive-freeze-design-checks.json`
- `outputs/Digitone-OS1.44E03-freeze-atomic-acquire-checks.json`
