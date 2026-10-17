# USB producer stop and outstanding transfers: static follow-up

## Finding

A receive-gate restoration barrier is still not established. The stock USB completion and buffer-release paths both lead back to receive replenishment. The recovered shutdown routine clears the outstanding counter after running descriptor cleanup; a zero counter by itself does not certify an empty deferred queue or stopped producers.

This follow-up is static analysis of stock 1.44 MAIN, with seven checked instruction encodings/branch targets. No new ColdFire execution tests ran: local Capstone/Unicorn dependency reads were denied even after an additional read-access grant. The standalone decoder and firmware binary were accessible. The earlier executed USB tests remain separate evidence.

## Recovered paths

`4000465a` attempts to replenish toward two outstanding receives using counter `40529258`. It claims a buffer-pool bit in `40529250`, obtains a descriptor through `40005bfc`, sets the receive buffer and callback `4000472a`, submits through `40005f1e` for endpoint index 1, then increments the counter. Within this recovered routine no receive-gate or independent stop-lease check appears. The code's call to submit and counter increment are not proof the hardware accepts the descriptor; lower-layer eligibility and return behavior still need execution coverage.

Completion `4000472a` decrements the counter. A positive length queues decoder `4000499c` through actual deferred enqueue `40001424`. Both the positive and nonpositive completion paths then branch to replenishment at `4000474e`. Thus counting hardware completions separately from deferred decoder work is necessary.

Buffer release `40004962` clears the corresponding pool bit, queries endpoint 1 through `40005f04`, and branches to replenishment at `40004996` if that query returns no descriptor. The periodic callback ending at `400047de` also branches to replenishment. Stopping only completion-driven rearming would leave these additional callers.

Shutdown/reset routine `40004806` clears register `fc0b01c4`, requests operations through `fc0b01b4`, polls bits 1 and 17 until clear, and calls descriptor cleanup `40005e42` for endpoint indices 5 and 1. It removes the periodic callback handle through `40006dde`, then clears `40529258`. The register roles and hardware acknowledgment semantics are not newly certified here; polling is not an established device-wide or deferred-work barrier.

Descriptor cleanup `40005e42` traverses the endpoint chain, obtains its saved callback and arguments, performs descriptor release through its function pointer, then invokes the saved completion callback at `40005ed4` when non-null. It clears the endpoint head/tail after traversal. Consequently, cleanup is not inherently callback-free: whether any descriptor callback can submit new work during this process requires lower-layer execution and hardware-precondition checks. Do not assume that endpoint cleanup silently discards every receive payload.

Recovered outer callers `40003a1e` and `400044ec` invoke `40004806` as part of broader USB shutdown. Their earlier shutdown calls may supply additional protection; this follow-up does not certify it. Initialization `4000487a` also calls `40004806`, clears pool/counter state, rebuilds descriptors, and calls replenish at `40004918`. Flag `40529230` selects receive length (64 versus 512); it is not a recovered stop flag.

## Conditions still required before restoration

1. Prevent every replenishment entry while owning the freeze, including completion, buffer release, periodic work and initialization. Establish lower-layer endpoint cancellation/acknowledgment before declaring transfers stopped.
2. Account separately for active descriptors, callbacks currently executing, queued deferred USB work, decoded input queues and partial frames. Previously executed tests already show MIDI queues can be empty while deferred USB work later mutates the receiver.
3. Permit responsible tasks to finish without draining a shared work queue recursively from its own worker. Verify no late callback can publish after the final cleanup check.
4. Preserve the lease against stock view-entry gate enables, initialization writes and stale failure cleanup. Only an owner-controlled, pre-flash rejection may restore the saved gate state; unknown failures and post-flash exits stay frozen.

These are requirements, not an implemented firmware barrier. Secondary USB-cable routing remains unresolved. Next is executing descriptor cleanup and lower-layer submission from controlled states, followed by the outer shutdown calls and callback ordering. That execution requires repairing access to existing analysis dependencies. Physical endpoint timing/cache coherence, reserved memory ownership, startup failure handling and flash-error handling remain independent gaps.

## Artifacts and preservation

Read-only source inventory: `work/audit-E03-USB-producer-static.py`.
Raw instructions, literal matches and static checks: `outputs/Digitone-OS1.44E03-USB-producer-static-inventory.json`.
No firmware file was edited, rebuilt, transmitted or installed. This report does not authorize hardware testing.
