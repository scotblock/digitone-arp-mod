# Digitone OS 1.42: update marker storage and missing-context behavior

**Follow-up:** [Storage lifetime and writer exits](Digitone-OS1.42-storage-lifetime-and-writer-exits.md) closes ordinary queue lifecycle coverage in the recovered paths and maps 20 normal exit states across 11 routines, including two tail transfers. Global aliases and actual exception cleanup remain unverified.

**There is now a concrete eight-byte storage candidate and a tested fallback policy, but storage is not yet certified globally unowned.** The candidate is payload space in the queue's fixed end record. The recovered queue uses its link word and stops before consuming its payload. This is stronger evidence than an arbitrary cleared RAM gap, but still requires a complete alias/lifetime audit before firmware edits.

The proposed policy preserves note delivery and raw release/allocation identity while declining new scale capture during an incomplete update. It does not silence the queue, wait for a writer, flush pending notes or acquire context later from another pattern. Firmware remains unchanged.

## 1. Storage audit

Queue initializer `400efc56` constructs two 20-byte end records:

| Record | Link word | Remaining payload range, exclusive end |
|---|---|---|
| Tail/end record | `4199d50c` | `4199d510..4199d520` |
| Head record | `4199d520` | `4199d524..4199d534` |

The tail initially links to the head and the head links to the tail. The 64 ordinary queue nodes are separately linked from `431dbfb8` through the exclusive end `431dc4b8`; neither end record is in that free pool.

At `400eff72`, the emission loop compares its next record with the tail pointer in `431dc4c0`. The equality branch at `400eff78` exits **before** reading timestamp `+10` at `400eff7c` or track `+0c` at `400eff86`. Therefore the tail's apparent note/velocity/track/time fields are not consumed as note payload in this path.

Append operations `400efede`, `400efee6` and `400efee8` alter link words. Removal at `400f0012` and `400f001c` also alters link words. The end record's payload is preserved by these recovered operations. Reclamation at `400f002a` changes an ordinary node's link after that node has passed the tail exclusion test.

Candidate placement:

- `4199d510`: 32-bit nesting depth.
- `4199d514`: 32-bit readiness/failure state.

No literal references to the four payload word addresses `4199d510`, `4199d514`, `4199d518` or `4199d51c` were found anywhere in decoded section 3. A nearby-address literal inventory identifies queue timing fields before and after the records; none supplies a direct payload owner. This inventory does **not** rule out computed pointers, generic bulk operations, alternate subsystem lifetimes or indirect consumers.

The candidate is inside the startup clear range `40242000..431dc690`, so it begins zeroed. Zero is deliberately an **unready** marker state in the PC design. Explicit initialization would still be required before capture is enabled. Queue construction is called at `4009bd08`, before the audio vector installation at `4009bd52`; this identifies an ordering boundary to investigate, not a completed implementation.

Do not rerun the stock queue initializer to reset the marker. It links onto an existing free-list head without clearing that head and is not established as safe against a live queue. Marker recovery would be a separate, proven operation.

Other storage choices remain less resolved: existing note/event fields cannot safely provide a persistent global writer guard; stack storage is not shared between task writers and the interrupt reader; managed heap allocation still needs a safe persistent pointer owner. No arbitrary RAM reservation has been approved by this audit.

## 2. Proposed marker semantics

Use one conservative global marker initially: any participating pattern update blocks new descriptor snapshots, even if its destination is currently inactive. This avoids assuming a stable bank identity while a pattern switch occurs, at the cost of potentially declining more snapshots. It is a V1 proposal, not a recovered stock behavior.

The state word distinguishes uninitialized, ready and invalid-after-failure states. The PC example uses readiness tag `0x534c4300` and a failure bit; this encoding is illustrative. Capture is allowed only when the exact ready state is present and depth is zero.

Entry and exit need short protected read/modify/write operations that preserve the caller's previous SR. Set depth **before the first destination write**. Restore interrupt state before the long update; do not mask the full pattern copy. Decrement depth only after the enclosing update is complete or its failure has been handled. Nested entry increments depth, so inner completion cannot falsely announce that the outer update has finished.

A failure before any destination mutation can balance the depth without marking data invalid. Failure after a write latches invalidity. A later successful update, including an unrelated bank update, cannot clear that latch: it may not have repaired the partially written backing. Recovery requires evidence that every affected backing is coherent and all writers are quiescent. No stock recovery path meeting that requirement has been established yet.

Overflow, unbalanced exits and unsupported state fail closed. The model's scope IDs diagnose cleanup errors on the PC; no additional firmware token storage is assumed.

## 3. Reader and musical fallback

The proposed descriptor reader performs one bounded protected read of marker state/depth, receiving pointer and all four root/scale pairs. That protects the read from participating concurrent writers; it cannot compensate for a writer that has not entered the marker protocol. All writer contexts, including any higher-priority interrupt writers, still need coverage.

| Situation | Proposed behavior |
|---|---|
| Ready marker, zero depth, valid receiving fields | Capture four contexts once and reuse them for descriptor items |
| Busy, unready, failed marker or invalid fields | Publish ordinary raw-note words with no new scale snapshot |
| Busy ends before the note is emitted | Keep that note contextless; do not capture from the later pattern |
| Note already captured before the update | Preserve its saved context through emission and copying |
| New accepted arp identity has no context | Clear retained candidate context and use stock pitch behavior |
| Contextless additive input keeps the existing identity | Preserve the context already accepted for that identity |
| Lower-priority input is rejected | Preserve accepted retained context |
| Release or MIDI-track item | Preserve stock routing/identity and do not attach synth-scale context |

The guard applies to **new pattern snapshot acquisition**, not every subsequent arp tick. Disabling valid retained context merely because a different pattern update is busy would lose the original-generation behavior already modeled. Stock stop/reset and arp identity checks still determine whether a retained context is usable.

The fallback retains the note itself. Missing context means the proposed scale lock is bypassed for the new contextless identity; it does not mean forcing chromatic metadata into an old identity or silently looking up the current destination scale later.

## 4. Writer boundaries to audit next

| Recovered operation | Candidate scope and remaining concern |
|---|---|
| Record replacement `40025628` | Enter after acquiring/validating the record and resolving backing, before the copy at `400256ec`; balance every exit after entry. Getter returns at `400256da`. Related-data writes and notifications must be included or proved independent. |
| Pattern default method `400208a0` | Enter before `400134e4` at `400208bc`; leave after complete initialization/notification. Direct initializer callers also require coverage. |
| Import converter `40008de0` | Validate pointers/header first; enter before destination work beginning at `40008e04`, then leave on every applicable return. Wrapper and per-track fallback defaults may nest. |
| Metadata restore/reset writers | Include the previously traced multi-store updates; a marker on large copies alone does not protect these. |
| Other direct default/conversion producers | Establish callers and participate or prove the destination cannot be read during capture. |

These are logical boundaries only. No instruction sequence, branch overwrite, register allocation or binary patch has been produced. Callback re-entry, allocation failures, exception/unwind exits and every early return still need concrete hook coverage. Nested depth is a design requirement precisely because wrappers and inner helpers can both participate.

## 5. PC and byte verification

The new busy-capture suite passes **14 scenarios**, including nested success, pre-write versus partial-write failure, persistent invalidity, recovery requirements, overflow/double exit, raw-note fallback, delayed emission, retained identity rules and all 64 queue-node append/removal operations. The modeled end-record payload survives those link operations and is never emitted as a note.

All **11 PC suites pass: 109 scenarios in total**, with their existing exhaustive encoding and musical checks. This pass verifies **26 exact executable byte anchors** for end-record construction/exclusion, link writes, initialization ordering and candidate writer boundaries. Tests model proposed behavior; they do not execute the processor or establish global RAM ownership.

Results are saved in `Digitone-busy-capture-check-results.json`; the PC specification is `digitone_busy_capture_checks.py`.

Unchanged SHA-256:

- Original SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

The next static target is **complete ownership/lifetime coverage for the end-record payload and balanced writer exits**, including exception paths. Safe storage certification, register/stack preservation and audio timing remain gates before any firmware modification.
