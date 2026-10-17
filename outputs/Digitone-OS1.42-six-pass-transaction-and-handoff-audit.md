# Digitone OS 1.42: six-pass transaction and queue handoff audit

**Follow-up:** [Outer pattern protection audit](Digitone-OS1.42-outer-pattern-protection-audit.md) traces explicit UI replacement, fallback reset and import callers. No complete-update guard was recovered in those routes. It also separates the unproven reachability of `40022552` from the demonstrated UI replacement path.

The current writer check and five follow-up checks are complete within the recovered paths. The main new findings are **historical-format false positives, additional current-pattern writers, and a distinction between per-track pair consistency and complete-pattern transaction consistency**. No complete firmware-wide update guard has been established. Firmware patching remains premature.

The original SysEx and decoded executable are unchanged. No firmware was modified, rebuilt, repacked, transmitted or flashed. New files contain analysis and PC specifications only.

## 1. Remaining writer and format checks

The legacy-to-current track converter `400089fa` really writes current root at `40008ac8` and scale at `40008b18`. Root comes from legacy `+3c6` and is restricted to 0..115, otherwise replaced with 60. Scale comes from signed legacy `+3c9` and is restricted to 0..34, otherwise replaced with -1. These are separated stores; checking value ranges does not prove that a pair belongs to one completed update.

Its whole-pattern wrapper is **`40008de0`**, not `400088ca`. The latter only copies 0x21 bytes. The wrapper requires serialized header value 10, loops eight tracks at stride 0x3d0, builds the expanded parameter area and writes the pattern index at current offset 0x16119.

The reverse converter `40008b70`, called by `40008f5e`, writes serialized layout 10. In that destination, `+3cb` is a **word copied from current length `+3c5`**, while `+3ce` comes from current velocity `+3c8`. Serialized root and scale are at `+3c6` and `+3c9`. Consequently, writes to the same numeric offsets in this converter are not writes to the active pattern's current root and scale.

Three other apparent writers belong to historical conversion wrappers:

| Track helper | Wrapper | Header transition | Track strides, source → destination |
|---|---|---|---|
| `4000add6` | `4000aeac` | 2 → 3 | 0x3ce → 0x3cf |
| `4000af40` | `4000b058` | 6 → 7 | 0x3cf → 0x3cf |
| `4000b0e8` | `4000b1c4` | 9 → 10 | 0x3cf → 0x3d0 |

These operate on serialized formats, not the current 0x1611d-byte pattern backing. Their offset matches alone must not be added to the current root/scale writer list. The complete historical conversion dispatcher remains outside this bounded classification.

The current default helper **`4001330c`** separately writes root 60 at `40013348` and scale -1 at `40013358`. Whole-pattern initializer `400134e4` invokes it for all eight tracks. Pattern-object method `400208a0` retrieves the object's actual backing and calls this initializer before notification. This is a real current-backing writer; it cannot be assumed to target temporary storage.

The resolved pattern backing getter is `40134ff0`: load object `+10`, then return. Table entry `40173e3c` identifies this getter alongside binder `4001fc74`. It contributes no copy or lock. Track default trampoline `400333ce` also reaches `4001330c`, but no caller was established in this pass; its mere presence does not prove an active execution route.

## 2. Whole-pattern copies and ownership

`40022552` resolves destination and source pattern objects, retrieves both backings and copies **0x1611d bytes** at `400225cc`. The first copy argument is destination. Thus selecting a canonical destination whose backing is the installed receiving bank can overwrite that active bank. The recovered function has no local SR mask around the copy. Its callers' complete transaction protection has not been proved.

The import path at `40024384` is another current-backing writer: it obtains project backing, computes `P + 0x1c + 0x1611d*index`, and calls `40008de0` with serialized input. Its temporary allocation is for the serialized input; that alone does not make the destination inactive. Notification follows conversion.

The recovered replacement path at `400256ec` copies 0x1611d bytes from an acquired record at `record+4` into the selected pattern backing. Capture/export copies at `40025508`, `40025b7a` and `40025cf8` run in the opposite direction; exporting a pattern is not an active-pattern overwrite. Ownership direction matters more than the shared size constant.

The copy helper `400ec23c` reads and writes groups of four longwords using MOVEM, then handles longword and byte tails. Relative to the beginning of a current pattern copy, a track's root and scale both lie in its 16-byte block at `track*0x3d0 + 0x3c0`. A model interrupted only between completed chunk instructions therefore preserves each track's pair. This does **not** establish bus-level atomicity or the consistency of an entire pattern: an interrupted copy can leave earlier tracks new and later tracks old.

No universal outer guard was proved for these operations. The nearby `40137012` routine acquires a record through type checking and reference-management calls; its presence is not evidence of an interrupt-exclusion lock.

## 3. Candidate protection boundaries

For an isolated root/scale update, the smallest relevant boundary surrounds all stores belonging to that pair, after values and one backing pointer have been resolved. Save and restore the caller's actual interrupt state. Allocate, convert and notify outside that bounded interval. This remains a design proposal, not patched instructions.

For the default helper, pair writes occur at `40013348` and `40013358`; related metadata writes continue through `4001336a`. For the converter, pair writes occur at `40008ac8` and `40008b18`. Any implementation would have to preserve register liveness, condition-code behavior and the other metadata semantics. A short mask inserted around an arbitrary subset of stores is not sufficient evidence.

Whole-pattern reset/import/copy needs a transaction decision beyond separate protected track commits. Two PC-only candidate policies were checked:

1. Build a genuinely inactive destination, then publish a complete receiving backing at a bounded boundary. Ownership, object bindings and lifetime of that bank still need proof.
2. Mark the complete transaction busy; the interrupt reader immediately declines snapshot capture while busy and continues with the defined missing-context behavior. It must never spin waiting for the interrupted writer. Storage, nested updates, failure cleanup and every participating writer still need proof.

Masking an entire large conversion/copy is not justified without an audio timing budget. A pointer check, CRC or repeated read cannot by itself recognize a semantically incomplete update whose bytes are otherwise valid. Whether V1 requires one generation for the entire descriptor's four-track snapshot, or only a completed pair for each track, must be kept explicit; the model tests the stronger whole-transaction policy separately.

## 4. Expanded PC transaction model

`digitone_transaction_handoff_checks.py` passes **12 scenarios**, including:

- A mixed root/scale pair whose individual values remain valid.
- **5,651 completed-copy checkpoints**, distinguishing intact individual pairs from mixed whole-pattern generations.
- Eight partial byte checkpoints under a proposed transaction-busy policy.
- Separate protected track commits versus a complete staged publication.
- Actual receiving backing versus a same-index canonical backing.
- Four queued contexts retained across a later pattern change.
- Pattern-union reuse, node recycling, release notes and full event remapping.

These tests specify expected behavior. Busy fields, staging storage and publication rules are proposed; they are not recovered stock firmware features. The model does not execute ColdFire instructions or measure interrupt latency.

## 5. Queue-to-event handoff and publication order

The queue producer zero-extends the raw note and stores its full word at `400efe94`; velocity follows, then track at `400efeac`. Completed nodes are linked at `400efede..400efee8`. A proposed compact context encoder needs validated track and velocity **before publication**. Simply replacing the note store at `400efe94` would be too early unless those inputs were explicitly obtained first.

At emission, raw node byte `+7` goes to event byte `+18` at `400effca`. The event is submitted by `400efff8..400efffa`, and the node is reclaimed afterward at `400f0024`. The candidate expanded event context must be written or cleared before that submission, independently of the node's subsequent reuse. Preserve the raw note used for allocation and release identity.

Allocator `400f0626` clears type and selected link/reference fields, but does not clear proposed event context `+20..+27`. A type-2 pattern event can previously own pointers there. Every applicable note producer must therefore initialize those bytes, or a justified common allocator change must do so; marker/CRC alone does not establish freshness. This pass confirms the queued path's publication boundary, not complete producer coverage.

The PC handoff tests demonstrate independent event copying before node reuse and context clearing for releases and unmarked notes. Full remapping preserves source context and raw note; retained acceptance still needs the already modeled source/destination binding guards.

## 6. Consolidated verification and remaining gates

All **10 PC suites pass, totaling 95 scenarios**. Their existing exhaustive encoding and scale checks also ran. This batch independently verifies **37 exact executable byte anchors** for conversion headers/strides, getters, copy instructions and queue/event order. Anchors establish correspondence with this OS image, not correctness of a firmware patch.

SHA-256 remains:

- Original SysEx: `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
- Decoded section 3: `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`

Results are saved in `Digitone-six-pass-check-results.json`. The safest next static target is the **outer caller/protection chain for `40022552`, `400208a0`, `40024384` and `400256ec`**, especially whether replacement commits can target the installed receiving backing and whether an existing bounded invalidation/transaction mechanism covers the complete operation. Safe storage, all event producers and final instruction/register integration remain separate gates. No flashable firmware should be produced at this stage.
