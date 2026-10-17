# Selected callback versus cancellation task

## Result

Four controlled PC ordering cases pass. On the recovered task-service route, cancellation does not run inside the selected USB callback interval in these executions: an injected interrupt finishes its callback and executes its return before the interrupted cancellation task resumes and notifies completion. An interrupt after cleanup finds an empty chain and adds no old callback.

This establishes the tested serialized ordering, not complete exception/scheduler exclusion. Nested interrupts and a scheduler handoff from interrupt context are not yet exercised or excluded. No claim of physical hardware readiness is made.

## Cancellation runs from a task service list

Actual registration `40002ecc(40007650,4)` produced node `429f21bc`, with callback `40007650`, mask 4 and a null next link in the test fixture. Actual service task entry `40002e6e` executes its counter/mask loop, follows list head `40528624` and invokes the cancellation processor at `40002eb6` when the counter-change mask intersects the node mask. Registration mask 4 is a service-selection mask, not an interrupt level.

Static task construction at `40003040` passes entry `40002e6e` to `4000170c`, with stack-size argument `800` and argument `0a` in the task-constructor position used for task priority elsewhere. `4000305a` readies the task. The separate tick interrupt `40002e40` signals its wake mechanism. These traces distinguish the task callback from direct USB interrupt invocation; full RTOS/task initialization and natural scheduling remain unexecuted here.

## Executed ordering

Two fixtures use incoming USB interrupt levels 3 and 4, each with two orders:

1. **Cancellation finishes first.** The actual registered service list invokes stock cleanup, which calls the completed descriptor's normal callback and then the cancellation notification. A subsequently injected USB interrupt sees an empty endpoint chain and returns without a second callback.
2. **USB interrupt preempts cancellation before cleanup.** The service task stops at `400076c4`, immediately before invoking descriptor cleanup. A format-4 interrupt frame records that continuation. Stock USB entry `400073ac` selects callback `4000472a`, updates/removes the endpoint chain, invokes the callback, and reaches `40007614` RTE. The emulator exception-return support restores the interrupted task continuation. Cancellation then resumes, finds no descriptor to callback again, and invokes its notification. Recorded order is selected-callback site → callback → interrupt return → cancellation notification.

Both levels and both orders produce exactly one receive callback and one notification. With the host replenish guard and receiver gate held, deferred/input work drains with no new submissions and an outstanding count of zero. The return uses the engine's installed exception/RTE support; physical exception entry, vector priority selection and controller acknowledgment are supplied fixtures.

## Remaining selected-callback gap

The USB dispatcher saves callback/length/buffer before chain removal, temporarily masks to IPL7 around removal, restores the incoming interrupt SR, then invokes the saved callback. The test confirms that a task interrupted before cleanup resumes only after that callback and RTE in the injected sequence. It does not certify every instruction boundary or higher-priority exception path.

Kernel signaling can request scheduling through a write to `fc050014`: the recovered semaphore signal `400018d0` updates ready-list state and sets bit 13 when a waiter exists. It contains no direct context-switch call in the recovered instructions, but the interrupt requested by that write could matter. The existing fixtures stub wake/lock behavior and do not create an eligible waiting cancellation task inside the callback. Therefore, no proof yet rules out a nested scheduler interrupt/handoff during the selected-callback interval.

Next is to trace that scheduling-request interrupt's configuration, priority, handler and return policy relative to USB, then exercise a real eligible waiter/ready task at the callback boundary. Full timing, hardware acknowledgment, memory visibility, alternate USB route, and continuous restoration coordination remain unresolved.

## Reproduce and preservation

- `work/test-E03-USB-callback-ordering.py`
- `outputs/Digitone-OS1.44E03-USB-callback-ordering-checks.json`

Service registration/list traversal, task callback loop, stock cancellation processor, USB interrupt body/callback and exception return execute. Task wake/locks, timer/task teardown, register state, host guard and notification remain fixtures. IRQ levels are test candidates and are not certified boot values. The script exits nonzero on assertion failure. Firmware files are unchanged; no device I/O occurred.
