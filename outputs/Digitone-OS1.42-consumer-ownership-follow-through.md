# Digitone OS 1.42: consumer ownership follow-through

Firmware remains unchanged. The original SysEx and decoded section 3 match their recorded SHA-256 hashes. No patch or flashable firmware has been produced.

## Result

The disabled-arp consumer does not supply a missing payload retain in the tested idle-voice state. Executing its actual note route before normal retirement preserves the earlier replay-counter underflow. This narrows the consumer uncertainty; it does not reproduce a fault on a Digitone.

## Consumer execution

The bounded interpreter enters `4009dc5e` with the published event in `a3`, track in `d2` and scheduling node in `a4`. It executes until common completion at `4009cef0`. Stock event release `400f065c` and scheduling-node retirement helpers execute separately in the recovered order.

Controlled inputs use the actual cache builder/publisher, modes 2/3 and last/lowest/highest selection. Arp settings byte `+10f` is zero, voices are initially idle and DSP synchronization is clean. Upstream descriptor construction, task scheduling and interrupt entry/exit are outside this execution.

All six combinations permitted:

`press A -> consume A -> press B -> consume B -> release B -> consume departing B and replayed A`

A seventh case completed all producers before consumption. Across 28 event routes, the actual note-on, note-off and replay paths reached common completion, preserved the event address and payload pointer, made no writes into the pointed record, and omitted template capture. Retirement underflowed A's replayed record count to `ffffffff`.

**Correction to the earlier guard explanation:** disabled arp returns identity zero and clears its mode output. With the supplied reset output zero, `4009ddb8..4009ddbe` branches directly to `4009df0a`; it does not visit the identity guard at `4009de12`. The executed route itself establishes that template capture is absent in this case.

## Parameter playback and voice cloning

The confirmed parameter-application graph at `4009b600..4009b69c` has 52 instructions and no calls. Execution with valid parameter indices 0 and 78 for each of eight voices wrote the expected values while leaving the complete 1,284-byte record unchanged, including its reference count.

Voice-child helper `4009bd8a` was executed with allocation succeeding and failing. Success copies 72 bytes, clears child fields `+2c`, `+30` and `+38`, sets the generated-voice flag and inserts the child into the event chain. Neither outcome changes the original payload count. A successful child has no payload pointer to release.

These helper checks are separate from the idle-voice sequences. Active-voice synthesis has not been executed end to end.

## Static ownership inventory

Confirmed-entry graphs cover 541 note-route instructions and 166 additional instructions across five helpers. The route's direct payload accesses are reads at `4009dd1e` and `4009e1f8`; none of its direct event writes clears or replaces `+38`. Its explicit retaining operation is conditional arp-template copy through `400f0690` at `4009de40`.

This inventory does not certify every transitive synthesis callback or global alias. The state synchronization gate can call `4009e4a8` when dirty; that branch was not executed here.

## Validation and next prerequisite

167 assertions passed across seven consumer sequences and ten helper cases, totaling 13,683 instruction steps. The prior 50-check payload-lifecycle and 51-check producer-ordering suites also pass after extending the interpreter with SWAP and BTST. Both firmware hashes remain unchanged.

The interpreter is a bounded analysis tool, not an independently validated ColdFire emulator. Enabled-arp acceptance, active-voice synthesis, upstream UI behavior and hardware interleaving remain outside these results. They do not establish a demonstrated stock-device defect.

For V1, keep root/scale snapshots independent of cached payload `+38`. The next prerequisite is the proposed explicitly allocated trailer's cold initialization/publication and reset/re-entry lifetime. Stock initialization publishes the pool owner before clearing and rebuilding it; a proposed trailer must be initialized before readers can observe it. An empty queue alone does not establish quiescence because retained templates and cached events have separate lifetimes. No storage placement or hook is certified yet.

Details are saved in `Digitone-disabled-arp-consumer-execution-results.json` and `Digitone-consumer-ownership-graph-results.json`.
