# Digitone OS 1.42 — owned payload storage audit

Read-only analysis, 3 October 2026. Proposed trailer remains `P+0x14100..P+0x14110`, where `P = *(4199d590)`. Firmware is unchanged.

**The audited parameter producer, playback consumer, record allocation/release and common event-copy routes stay clear of the proposed trailer under their recovered valid-input contracts.** The enclosing heap allocation is not freed by record recycling. A second initialization-wrapper caller was recovered, so the initializer cannot simply be described as startup-only. Its external reachability and safe reset conditions remain unresolved.

## 1. Parameter producer has an actual bound

Both recovered record-pop callers (`40093e90`, `400dc5c8`) pass the record to `40093bd4`, directly or through the reused-event path. A confirmed-entry control-flow graph for that producer contains no calls.

The producer iterates source indices 0–78. For each nonempty value, it writes two words at:

`record + 0x14 + output_index × 8`

The number of emitted entries cannot exceed 79. It stores that number into record `+08`. The maximum written end, excluded, is:

`0x14 + 78 × 8 + 4 = 0x288`

That is inside the `0x504` record. Even the final record cannot reach trailer start. This is stronger than assuming the nominal 158-entry capacity is always respected: this particular firmware producer has a smaller proven loop bound.

The path at `40093e7a` can reuse an existing event's `+38` pointer instead of popping a new record. Its subsequent producer call has the same bound. This assumes that field points to a valid record; pointer provenance for every reused-event source is not fully closed.

## 2. Playback consumer reads the record; destinations are separate

The retained payload field reaches `4009b600` through:

- Direct call `4009e20a`, supplied by event `+38` at `4009e1f8`.
- Indirect call `4009dd2e`, with `a5` explicitly loaded with `4009b600` at `4009dc88` and the payload loaded at `4009dd1e`.

The consumer loads its record into `a2`, starts at `record+14`, and advances by eight bytes until it reaches the count at record `+08`. It reads the parameter identifier/value at each entry. Its writes are to separately derived parameter bitmaps, caller-supplied synth state and fixed DSP-state memory, not to the record itself. Its confirmed-entry graph is call-free.

For counts produced by `40093bd4` (0–79), its record reads share the producer's `record+288` maximum end. There is no local defensive clamp on a corrupted count; this is a producer-to-consumer contract, not proof of safety for arbitrary record contents. Destination-index validation for the separate synth buffers is outside this trailer-storage audit.

## 3. Record recycling is confined to record headers

`400f05d6` pops the free-list head, follows record `+10`, clears that link and increments the reference count at `+00`. `400f05f8` decrements the count and, when it reaches zero, writes the current free-list head at record `+10` and returns that record to the list. Neither routine calls the general heap free function.

The initializer installs exactly 64 record addresses at stride `0x504`. Its last record's `+10` link is null. Thus a valid free-list lifecycle returns ordinary records, including the last record, and never creates a record at trailer start.

Exhaustion is a separate existing hazard: the pop routine dereferences its head without a null check. A 65th pop with no release does not produce a valid trailer address; it encounters a null-head path. The PC model records that as outside valid stock lifecycle rather than pretending the firmware has a graceful exhaustion return.

## 4. Event retention and copying

Common event release `400f065c` calls record release only for event type 0 with a nonnull `+38` pointer. Common event copy `400f0690` releases the old destination's type-0 payload, increments the incoming source's type-0 payload reference, then copies 72 bytes of event data. The reference increment writes only record `+00`.

The recovered callers copy a retained template into a new event (`4009ce3c`) or update a retained template from an event (`4009de40`). Neither copy writes the payload array or trailer.

Clone helper `4009bd8a` performs a raw event copy but explicitly clears the clone's payload pointer at `4009bdb4` before publishing it into the event chain. That route does not create an extra payload-owning event.

Ownership is type-dependent: type-1 reuse is not governed by the type-0 retain/release checks. The audit does not claim that every raw event copy establishes a balanced reference. The other raw-copy routes and typed event sources require separate provenance checks before declaring full record-lifetime coverage.

The nearby type-2 producers at `40094f2e` and `400959a6` put `41342218` into event `+38`; that is a different union meaning. Likewise the scheduler's type-2 forwarding at `4009cc52` is not evidence of this heap pool escaping. A broad search found 110 candidate loads of object `+38`, many belonging to unrelated objects and virtual tables; matching a field offset alone does not identify a payload consumer.

## 5. Initialization correction: a second wrapper call exists

The initializer still has one recovered direct transfer, `4009bcbc`, inside wrapper `4009bcb8`. However, that wrapper has **two** recovered callers:

| Caller | Recovered behavior |
|---|---|
| `4009bcec` | Normal setup before audio-vector installation |
| `4009bdec` | Inside `4009bde8`, followed by allocation and submission of events with conspicuous test values such as `12345678` |

The second routine appears test-like based on its visible behavior. The expanded direct-transfer and exact-pointer searches found no external entry into it, but do not prove it unreachable. It must remain in the reset audit.

On a nonzero persistent owner, initialization skips allocating/clearing the enclosing block but rebuilds the payload, event and scheduler free lists. It resets record reference counts and links. Therefore live reinitialization can invalidate retained records independently of the trailer.

The correct proposed requirement is **quiescent initialization**, not merely "initialize once because the owner is nonzero." Reset must be excluded while events retain records or a pattern transaction is active. Trailer readiness must be invalidated before any permitted reconstruction. No such guard exists in the stock routines or was installed in this investigation.

The prior alternative report's constructor-entry count was correct, but its startup framing was incomplete: this additional wrapper route is now explicitly tracked. It does not change the 64-record layout or calculated allocation footprint.

## 6. Verification and decision

This pass traverses confirmed-entry instruction graphs for seven routines: the parameter producer, playback consumer, payload pop/release, common event release/copy and pool initializer. Together they contain **213 reachable instructions**. Calls in these graphs are treated as returning normally; this is not exception or hardware execution analysis.

Verification checks **26 exact instruction anchors** and **13 PC specification checks**, covering all 64 record positions with counts 0–79, complete allocation/exhaustion, retained references, final release, recycling and reset rejection with active transactions or retained records. The checks pass. Machine-readable evidence is in `Digitone-owned-payload-lifetime-audit-results.json`.

**Decision:** continue with the explicitly requested trailer. The recovered write bounds and ordinary recycling support it more directly than the old queue-sentinel candidate. It is not yet ready for implementation: close the remaining typed event-pointer/copy routes and the extra setup route's reachability/quiescence, then audit an exact initialization integration with allocation failure and register/stack preservation. General allocator emulation and balanced pattern-writer exits remain separate checks.

No firmware modifications, rebuilt firmware, flashable artifacts, device traffic or hardware tests occurred. Input hashes remain:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`
