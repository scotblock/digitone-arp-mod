# Digitone OS 1.42: storage lifetime and writer exits

**The recovered queue lifetime and ordinary writer exits are now mapped. A full safety certification is still incomplete:** computed/global storage aliases and application exception exits are not proved. The marker remains a PC-only proposal; no firmware guard has been implemented and no binary was modified.

This pass finds two concrete implementation hazards: conditional entry paths share return epilogues, and two normal paths finish through tail transfers. A guard that simply decrements at each visible RTS would be incorrect.

## 1. Queue storage lifetime: closed within recovered paths

The proposed marker words are `4199d510` and `4199d514`, inside the payload of fixed end record `4199d50c`. Its link word must remain unchanged by marker code.

The recovered lifecycle is:

1. Startup clear zeroes this region. Zero means unready in the proposal, not an initialized guard.
2. `4009bd08 → 400f00ea → 400efc56` constructs queue links before audio-vector installation at `4009bd52`. Construction changes end-record links; it does not initialize the proposed marker payload.
3. Allocation uses only ordinary nodes in `431dbfb8..431dc4b8`, 64 records at stride 20. The fixed end records are outside that free pool.
4. Append alters the old last record's link, the end-record link and the new node link. It does not copy node payload into the end record.
5. At emission, `400eff72..400eff78` excludes the end record before accessing timestamp, track, note or velocity.
6. Removal updates links; only an ordinary node that passed the end-record exclusion is reclaimed. Successful emission and event-allocation failure both reclaim that ordinary node.

The recovered queue therefore does not allocate, emit, recycle or copy the proposed end-record payload as a note. The 64-node PC link/reclaim checks preserve it. No live reset through queue initialization is authorized: the stock initializer does not clear its existing free-list head and must not be rerun against a live queue to reset the marker.

The broader nearby-address inventory found 64 literal occurrences, identifying timing/state fields around the records. No exact payload-word reference was found. End-record pointers appear in construction; the queue-head pointers' recovered uses remain in construction, append, traversal and reclamation. No additional direct payload owner or recovered pointer escape was established.

**Boundary of closure:** this establishes the ordinary queue lifecycle, not global RAM exclusivity. Computed addresses, generic bulk operations and unrelated subsystem ownership still require coverage. Startup clearing, absence of literal references and the queue's local exclusion cannot individually prove that these bytes are safe for new global state. `global_storage_certified` remains false in the result file.

## 2. Normal exit map for participating routines

Branch traversal recovered **885 reachable instructions across 11 routines**, using instruction-level control flow rather than truncating a window at its first return. Call instructions are treated as returning normally; branch feasibility and exceptions are separate questions.

| Routine | Proposed entry point used for exit analysis | Ordinary completion |
|---|---|---|
| Metadata restore `40034a8c` | Before first destination field store `40034bb4` | RTS `40034c76`; entered and never-entered paths share it |
| Metadata record restore `40034c78` | Before `40034d00` | RTS `40034d9a`; both entry states |
| Metadata reset `40035268` | Before `40035356` | RTS `400353f6`; both entry states |
| Track defaults `4001330c` | After null rejection, at `40013314` | RTS `4001336e`; both entry states |
| Whole-pattern defaults `400134e4` | After null rejection, at `400134f8` | Null path RTS `40013562`; entered path tail branch `40013556 → 40013478` |
| Parameter-area clear `40013478` | After null rejection, at `40013488` | RTS `400134e2`; both entry states |
| Pattern default method `400208a0` | At `400208b8`, before initializer arguments | RTS `400208d8`; entered path |
| Pattern import `40008de0` | After pointer/header validation, at `40008e04` | RTS `40008eae`; both entry states |
| Track import `400089fa` | After pointer rejection, at `40008a16` | RTS `40008b6e`; both entry states |
| Whole-pattern copy `40022552` | Before copy arguments at `400225c2` | Indirect tail jump at `400225ea` to notification |
| Record replacement `40025628` | After backing resolution, at `400256dc` | RTS `40025794`; both entry states |

These are analysis points, not proposed replacement instructions. Register/stack preservation at any actual insertion site remains unproved. The copy routine's runtime reachability is also still a gap; it is included for candidate coverage, not presented as another demonstrated active UI operation.

The map has **20 normal exit states** and **two tail continuations**. An entered/not-entered state must be preserved or eliminated by restructuring the scope. Decrementing unconditionally at a common return would underflow on null/failed-record/pre-write rejection paths. Closing only at visible returns would strand depth on the two tail paths.

For whole-pattern defaults, a scope protecting the complete update must survive the tail call to parameter clearing. Closing before that tail transfer only protects an earlier subset of the update. Options are an outer wrapper with cleanup after the callee returns, or a deliberate call-and-cleanup continuation. Neither has been implemented.

## 3. Exception exits are not closed by the normal graph

The image contains `std::bad_alloc`, `std::exception`, forced-unwind type names and termination diagnostics. Those bytes establish exception-runtime material in the image; they do not prove that a particular writer throws or that its callers recover.

Several outer routines invoke record helpers, virtual notification methods and reference cleanup after proposed entry. In particular, `4012c344` can invoke virtual destruction through slots `+08` and `+0c`; its name or reference-count role does not prove that it cannot escape a caller normally.

No validated per-writer unwind/landing-pad map was recovered in this pass. Ordinary error branches, destructor calls and early returns are not equivalent to exception cleanup. **Balanced application exception exits therefore remain unverified.** This is explicit in the result data; no successful model test is being used to claim that stock firmware contains the required cleanup.

The new PC checks inject failure at **49 call sites structurally reachable after proposed entry**. Without an exceptional cleanup continuation, depth remains entered. With the modeled required cleanup, depth balances and partial-write invalidity stays latched. The injection count includes syntactically indirect calls, some of which have separately resolved simple getters; it is not a count of proven throwing calls.

## 4. Refine guard scope to reduce cleanup hazards

Four recovered data routines contain no call instructions:

- Copy primitive `400ec23c`.
- Clear primitive `400ec284`.
- Track defaults `4001330c`.
- Track conversion `400089fa`.

They do not call application exception code in their visible bodies. This does not certify invalid memory accesses, CPU faults, interrupt effects or argument validity.

For record replacement, a narrower **pattern-backing transaction** could begin after backing resolution and end immediately after the pattern copy at `400256ec`, before associated-data updates and callbacks. This covers the complete 0x1611d-byte pattern copy while avoiding later notification/destructor escape hazards. It does not promise an atomic combined pattern-and-associated-data transaction; whether that stronger scope is required must remain explicit.

For metadata restore/reset, the between-store getter is the already resolved call-free backing load `4013a33a`. Preparing one backing pointer and all field values before a bounded data commit, then notifying afterward, is a cleaner candidate than keeping guard state entered across unrelated allocation and cleanup. Such restructuring needs a separate equivalence and register-liveness audit before implementation.

Whole-pattern initialization/import still needs a scope across every relevant inner writer, including tail completion. Per-track scopes alone expose mixed generations between tracks. Nested accounting and balanced outer completion remain necessary for that stronger policy.

## 5. Verification and outstanding proof

All **12 PC suites pass: 115 scenarios**, including the new six exit/lifetime scenarios, 20 normal exit states, both tail continuations and 49 guarded-call failure injections. This pass independently checks **22 exact byte anchors**, the queue pointer inventory and the four call-free routines. The executable branch maps are saved in `Digitone-writer-exit-graphs.json`; detailed verification is in `Digitone-storage-lifetime-and-writer-exit-results.json`.

Original firmware hashes remain:

- SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

The requested ordinary lifetime and normal-exit checks are complete within the recovered paths. Global end-record storage ownership, actual exception cleanup, complete writer coverage and instruction/register integration are **not** closed. The next useful work is to resolve the remaining indirect cleanup/notification targets and choose data-only commit scopes where possible, rather than assuming a broad outer hook can safely unwind. Firmware modification remains premature.
