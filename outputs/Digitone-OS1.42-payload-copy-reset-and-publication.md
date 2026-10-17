# Digitone OS 1.42 — payload copying, reset and publication

Read-only follow-up, 3 October 2026. Firmware and decoded executable hashes are unchanged. Proposed storage remains an explicitly requested 16-byte trailer on the persistent 64-record allocation.

**This pass identifies a workable local-pointer route for delayed initialization publication and narrows reset behavior. Raw event-copy ownership remains unresolved:** scheduler publication does not itself retain the payload. No runtime reference-count defect has been demonstrated.

## Raw copy source and publication

`400efa20` takes a descriptor, builds a cached 72-byte event at `431d1758 + track*2a18 + 414 + slot*48`, and copies descriptor `+28` into cached event `+38` at `400efa90`. It clears the cached event's type word at `400efab8`.

The three recovered raw copy sites are `400efbe0`, `400efc08` and `400efc2a`. Each copies a cached event into a newly allocated event. They converge on scheduler publication `400f0886`; one route also publishes an earlier event separately at `400efbe4`.

The publisher writes scheduler/event links under a short interrupt mask. It does **not** increment the record reference count. Therefore the copy cannot automatically be treated as an additional owner. Its correctness depends on the descriptor/cache providing a transferred reference or a borrowed reference with a separately retained lifetime.

The previous common copy `400f0690` is different: it explicitly retains incoming type-0 payloads. Its contract must not be attributed to these raw copies.

A constructed PC example illustrates the missing obligation: copying one owning event into a second owning event without retaining gives two owners but one reference. Transferring one reference from a borrowed staging cache into one queued event is balanced. Neither example proves which contract the actual source follows. Establishing that contract is the remaining target.

## A separate four-record allocation

Initializer `40094852` allocates `0x1410` bytes, clears them, and installs four pointers at `419a38a4..419a38b4`, separated by `0x504`. This allocation is distinct from the 64-record pool owned at `4199d590`.

The pattern producer at `4009445c` can load an event payload pointer from that four-pointer table before calling `40093c26`, whose reuse path invokes the bounded parameter producer. Thus not every valid payload pointer necessarily comes from the 64-node free list. This distinction matters when modeling source ownership and when deriving trailer addresses: **the trailer must always be derived from the persistent 64-record owner, never from an arbitrary event payload pointer.**

These four record ranges do not extend the proposed 64-record allocation or its trailer. Their allocation/free lifetime remains a separate source-provenance question.

## Queue drain is not full pool quiescence

Routine `400f08f0` detaches scheduler head `4199fe94` under an interrupt mask, walks the detached event chains, invokes an optional callback, releases each event through `400f065c`, and returns scheduler nodes through `400f06d4`. It saves the next event link before callbacks/release.

Recovered caller `4009bd6a` supplies callback `4009ba94`, which handles type-3 event state via `400e42ec`. It then calls `4009713c` and tail-transfers to `400ef9d0`.

The confirmed body of `4009713c` clears arp note bitmaps and related arrays; it contains no calls and no references to retained templates at `41345f08`. This route does not establish release of every retained payload. An empty scheduler queue therefore cannot be used by itself to approve rebuilding the payload free list.

The proposed reset contract still requires no active pattern transaction, no producers/consumers in flight and no outstanding retained record owners, including arp templates. No reset guard has been installed.

## Additional setup routine: relative entry search narrowed

The test-like routine `4009bde8` calls setup wrapper `4009bcb8`. Earlier expanded direct-transfer and exact-pointer searches recovered no external entry into it.

The standard signed-word dispatch inventory has no table base within signed-word reach of that routine. One other nearby compiler expression uses `movea.w` to sign-extend a table entry into `a0`, then jumps relative to table `4009afe4`. Its unsigned selector bound allows five entries; all were checked. Their targets are `4009b16a`, `4009afee`, `4009b048` and `4009b0e0` (twice), excluding `4009bde8`.

This removes another concrete entry mechanism. It does not prove the routine unreachable through every computed or RAM-loaded address. Initialization must continue to account for this recovered internal route.

## Delayed owner publication can use a local pointer

The clear primitive `400ec284` returns its original destination argument in `d0` at `400ec2c8`, followed by return at `400ec2cc`. On the first-allocation path, that is the newly allocated pool pointer. It does not require the pointer to have been published globally before the clear.

The current initializer reloads `4199d590` at `400f059e`, because stock code published the pointer before clearing. A proposed control-flow split can instead:

1. On first allocation, request `0x14110`, reject null, clear through the local pointer and keep the returned `d0` pointer.
2. On reuse, load the existing owner into `d0`, but permit reconstruction only under the established quiescence contract.
3. Join the record-link construction with `d0 = P` and `d2 = 0x504`.
4. Initialize the trailer and publish the owner only after construction completes.

The record-link loop and final-record calculation preserve `d0` while computing addresses through `a0/a1` and the stride. `d3` carries the allocation/clear extent on the cold path; increasing that request does not require increasing `d2` or the record count. The original allocation-plus-clear argument area totals 16 bytes, and no additional RAM pointer holder is needed in this design.

This is a register-data-flow proposal, **not a verified instruction patch**. The actual branch insertion, existing/free-head publication order, caller expectations, register preservation and failure continuation must be checked before implementation.

Null allocation cannot simply mean "disable scale locking and continue": the same allocation supplies stock playback's required payload pool. A failure path must prevent construction and subsequent use of a missing stock pool. No suitable continuation has yet been selected or implemented.

## Verification and next work

The pass verifies 33 exact instruction anchors, the five nearby switch entries, the call-free bitmap-reset body, and 11 PC specification checks concerning borrowed versus transferred references, retained templates and initialization publication. These are specification examples, not execution of the actual firmware or its callbacks. Results are in `Digitone-payload-publication-followup-results.json`.

The next concrete work is to trace descriptor `+28` and cached event `+38` through publication/reuse, distinguishing the 64-record and four-record sources. In parallel with that source audit, the proposed cold-init control-flow split now has concrete register facts to validate. Reset quiescence and allocation-failure continuation remain explicit integration requirements.

No firmware modifications, rebuilt images, flashable files or hardware operations were performed.
