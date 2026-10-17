# Cancellation masks and completion dispatch

## Result

Nine controlled PC tests pass. Cancellation acknowledgment plus endpoint-chain removal excludes subsequent completion events from selecting the removed descriptor in the executed dispatcher. This narrows the earlier direct late-callback probes: a stale controller completion event alone does not reproduce a stale callback when the endpoint head is empty.

It is not yet a restoration certificate. Completed descriptors can deliver callbacks during cancellation; their deferred USB work remains at the cancellation notification. The submission block is cleared before that notification. A callback already selected/executing, actual interrupt ordering, and physical acknowledgment semantics remain unverified.

## Recovered stock flow

Cancellation request `40005e04(endpoint, notification)` sets the endpoint's bit in submission-block mask `429f23b8` and pending-cancel mask `429f23c8`, stores the notification in table `429f23cc`, and writes the corresponding controller mask to `fc0b01b4`. A repeated request while its pending bit is already set returns without replacing that notification.

Cancellation processor `40007650` scans eight endpoint indices. While the corresponding register bit remains set, it leaves cancellation pending. Once the supplied register state shows it clear, it calls descriptor cleanup `40005e42`, clears the submission-block bit, invokes the stored notification if present, then clears the notification slot and pending-cancel bit. Thus the notification runs after software submission has been unblocked, while the pending bit is still set. It does not drain the deferred-work queue.

Completion interrupt entry `400073ac` scans completion bits in `fc0b01bc`. It obtains the endpoint head, skips a null head and a descriptor with active-status byte `+7 == 80`, saves the callback/length/buffer, updates the chain under temporary IPL7, restores incoming SR, then invokes the saved completion callback. This recovered path does not use the cancellation masks to suppress completed-descriptor callbacks.

For descriptor cleanup, status byte `+7 == 0` selects normal callback `+24` with transferred length; nonzero status uses alternate callback `+28` if supplied. The tested active descriptor has a null alternate callback, matching the zero-initialized pool fixture. It is removed without invoking the normal callback. These status values are supplied test conditions; hardware update/visibility is not certified.

Static registration evidence: `40007272` loads interrupt entry `400073ac`, with vector/control writes following it; `400072aa` passes cancellation processor `40007650` to `40002ecc` with argument 4. This identifies separate dispatch routes, not their complete runtime ordering or priority contract.

## Executed checks

| Case | Observation |
|---|---|
| Cancellation register bit still set | No cleanup, completion callback or notification; both masks stay set. |
| Acknowledged cancellation of completed descriptor, unguarded | Normal callback executes; two replenish submissions return `ffffffff` while blocked, but stock increments outstanding count. Notification follows cleanup with masks in the recovered order and deferred input queued. |
| Same cancellation, host replenish guard held | No submissions; callback decrements count to zero; notification still sees one deferred item. |
| Completion event during pending cancellation | Dispatcher invokes completed descriptor's callback, despite pending/block masks. Later cancellation acknowledgment finds an empty chain. |
| Completion event after acknowledged chain cleanup | No additional old callback. |
| Completion event with initially empty head | No callback and no count underflow. |
| Acknowledged cancellation of active descriptor | Removes chain without normal callback; outstanding count stays one, notification fires with no deferred work. Thus count alone does not summarize canceled-descriptor cleanup. |
| Completion event for active descriptor while cancellation pending | Skips descriptor; masks remain pending. |
| Two completed descriptors | Cleanup delivers both callbacks, drains the chain and notifies with two deferred items. A subsequent completion event adds no callback. |

Receive gate stays closed in all cases, and subsequent deferred/input consumption leaves receive state/buffer unchanged.

## What is and is not established

The software exclusion condition tested is an empty endpoint chain before the completion dispatcher reads its head. A removed descriptor cannot be selected through that path. The previous direct invocation of `4000472a` after shutdown remains an adversarial contract probe, not evidence that this dispatcher naturally emits such a callback.

The dispatcher saves callback state before invocation. We have not proved that cancellation cannot overlap that interval, or that its notification cannot precede an already captured callback's completion. The harness invokes routines with incoming IPL7. Interrupt entry runs its stock prologue/dispatch but stops before saved-register restore/RTE; no natural interrupts, task priorities or exception returns execute. Actual controller register/descriptor acknowledgment and memory ordering are fixtures.

Next: establish the ordering between cancellation's registered service and the USB interrupt, including the saved-callback interval and timer/service registration. Then combine acknowledged chain cleanup, no callback in flight, deferred/decoded queue cleanup, partial framing and gate ownership in a continuous PC coordinator. Notification, cleared pending mask or count zero alone are insufficient.

## Reproduce and preservation

- `work/test-E03-USB-cancellation-dispatch.py`
- `outputs/Digitone-OS1.44E03-USB-cancellation-dispatch-checks.json`

Host-only guard/notification, completed payload, descriptor pools, controller event/acknowledgment registers and prior registry/heap/synchronization fixtures remain. The script exits nonzero on failure. Firmware hashes remain unchanged; no device I/O or flashable build occurred.
