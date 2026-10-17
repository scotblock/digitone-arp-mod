# Outer USB shutdown and late callbacks: executed PC tests

## Result

Ten controlled cases pass. Both recovered outer shutdown entries execute through their recovered USB cleanup and return under register-acknowledgment fixtures. Neither supplies a lasting software submission block in the tested initial state: the endpoint block mask remains zero, deferred work remains, and real buffer release can replenish after return. The host replenishment guard prevents those submissions while it stays active.

The guard is still insufficient as a restoration certificate. Explicit late completion probes decrement a cleared outstanding counter to `ffffffff` even when the guard blocks submission. Reopening the receiver gate before such a callback permits its payload to mutate the receive buffer, including with the replenishment guard still active. These probes establish required handling conditions, not natural hardware reachability.

## Executed outer paths

- `40003a1e`: register clear, stock `400034f6` and `40003560`, stock USB shutdown `40004806`, and tail call to stock `400051cc`. Endpoint lookup and descriptor cleanup execute. The tail routine's register polling is supplied explicit fixture values allowing its distinct CCR/bit checks to finish.
- `400044ec`: register clears, stock `4000409a` (including its tail call `40003f2a`) and `40004140`, followed by stock `40004806` and remaining timer/task cleanup.

Timer registration/removal (`40006d68`/`40006dde`) and unrelated task teardown (`40006f22`) are explicitly stubbed and logged. USB acknowledgment polling uses host fixtures. Endpoint chains, payloads and available descriptors are controlled; hardware prime/status register conditions remain fixtures. Natural mode-selection eligibility, actual canceled-descriptor delivery, producer scheduling and device acknowledgment behavior are not certified. Existing registry/heap/thread synchronization fixtures also remain.

For each outer entry, paired unguarded/guarded cases start with one queued descriptor and a positive completion payload. The receiver gate stays closed. At outer return the outstanding count is zero and one deferred work item remains. Without the guard, cleanup made two endpoint submissions and consuming deferred work makes two more, leaving count two. With the host guard active throughout, no submissions occur and the count remains zero. Receive state/buffer remain unchanged in all four paired cases.

The endpoint block mask `429f23b8` remains zero in these fixtures; absence of a block here does not exclude protection established earlier by application mode selection or controller state. Software submission under fixture registers does not establish physical transfer acceptance.

## Late and restoration probes

These six cases deliberately invoke a callback after an outer shutdown with no initial receive descriptor. They do not assert that hardware can deliver that callback after real cancellation.

| Probe | Observation |
|---|---|
| Late positive completion, guard/gate held | Queues deferred input. No submissions; receive buffer unchanged. Counter underflows from zero to `ffffffff`. |
| Late zero-length completion, guard/gate held | No deferred input and no submissions; counter still underflows. |
| Periodic callback, guard/gate held | Replenishment entry suppressed; count remains zero. |
| Guard released before late positive completion, receive gate held | Three submission attempts occur because the callback first decrements zero; afterward count is two. Receive buffer remains unchanged. |
| Both guard and receive gate restored before late positive completion | Three submission attempts and receive-buffer mutation occur. |
| Receive gate restored while replenishment guard remains held | No submissions, but queued late payload still mutates the receive buffer; counter underflows. |

A producer guard prevents new receive submissions, not delivery of already completed payloads. It cannot replace receive-gate ownership or an acknowledgment that no callback is pending/executing. A global zero count is particularly weak when stock shutdown forcibly clears that count.

## Next focused gap

Trace and execute the controller cancellation/completion dispatcher and the writers of endpoint masks, then establish when an old descriptor can no longer produce a callback. Audit the application path before the two outer entries for any additional exclusion. Verify timer callback removal/in-flight ordering rather than relying on the timer fixture. Only after those conditions are established can a continuous coordinator authorize owner-controlled restoration.

If late callback exclusion cannot be established, the prototype needs generation/ownership-aware callback handling with certified state storage; merely suppressing replenishment does not fix counter mutation or late queued input. That is a design alternative, not an implemented patch.

## Artifacts

- `work/test-E03-USB-outer-late-callbacks.py`
- `outputs/Digitone-OS1.44E03-USB-outer-late-callback-checks.json`

The script exits nonzero on assertion failure. Stock MAIN, E02 and E03 hashes still match recorded values. Firmware is unchanged, no device I/O occurred, and no hardware-ready claim is made.
