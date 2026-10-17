# Digitone OS 1.42: eligibility of cached replay with a payload

The recovered firmware branches permit a cached-note replay with non-null `+38`. The allocation gate is a persistent selected-step value, not simply whether an arp is running. Unselected notes and event-allocation failures have different ownership histories from notes that were already published.

This establishes branch-level eligibility and identifies concrete ownership hazards. It does not establish a reproduced stock-device defect or certify all controller/task interleavings. Firmware is unchanged.

## Payload allocation gate

For valid synth tracks 0–3, `4009e39e` returns true. In `400dc432`, that result makes `400dc5bc` take the parameter-record allocation branch whenever:

- the incoming note has passed the preceding input/suppression checks;
- global `401feafc`, interpreted unsigned at `400dc598`, is at most 63;
- the stock payload pool has a valid free record.

`400dc5c8` pops that record; `400dc5e8` places it in descriptor `+28`. The settings mode at `+12a` is not part of this allocation decision. Thus there is no local rule limiting payloads to modes that cannot replay cached notes.

The image's initial value at `401feafc` is `ffffffff` (−1), which fails the unsigned ≤63 comparison. A fresh descriptor then keeps `+28` zero. This explains why an ordinary live-note scenario can be payload-free, but does not establish that all live-note scenarios are.

### The selected-step value persists

Setter `400dcaf6` normalizes its argument to −1 or 0–63 and stores it at `400dcb06`. The recovered direct setter sites are:

| Site | Behavior |
|---|---|
| `400ab14c` | Tail call with the first selected index found in a 64-bit mask at object `+158/+15c`. |
| `400aa8c6` | Sets −1 when object selection mode is disabled and the previous value was nonnegative. |

The selection updater `400ab0ac` is called from a UI route at `40044630`. It returns without clearing the global when its mask is empty; the separate disable routine supplies the explicit clear. A nonnegative selected index is therefore persistent state, rather than a temporary value scoped around a note-builder call.

Exact user-facing labels for this mask/mode have not been established. The selected-step interpretation follows the 64-entry index and its use to fetch per-step parameter data.

### A live input route does not exclude that state

The MIDI Note On entry `400dc8c4` routes nonzero velocity to `400dc758`. Its per-track channel branch loads the note builder into `a5` at `400dc80e` and calls it at `400dc898`. Selecting a direct track-channel route avoids the optional mapped/auto-channel branches. The recovered direct branch contains no explicit call to the selected-step setter or selection-disable routine.

Together with the persistent setter, this is a viable branch-level route to payload-bearing live notes. The channel route and sound-selection setters do not provide a recovered mutual-exclusion rule. Full reachability through every outer controller and interrupt/task boundary is still outside this result.

## Cached replay is a valid mode branch

The sound-setting setter `4002f08a` clamps `+12a` to 0–3 and writes it at `4002f0e4`. Selector setter `4002f13a` clamps `+12e` to 0–2 and writes it at `4002f180`. Consequently values 2/3 for the replay mode, and all three selector values, are supported settings values rather than hypothetical out-of-range inputs.

At `400efaf8`, modes 0/1 use the ordinary current-note branch. Modes 2/3 use the selection branch. The recovered selectors choose the last inserted, lowest, or highest active note. If a note-off removes the selected note and another remains, `400efc08` copies the remaining note's cached event, including its existing `+38`.

The departing note's zeroed descriptor clears **its own slot's** `+38` at `400efa90`. It does not clear the remaining slot. The raw replay copy and scheduler publication add no payload retain.

## Ownership depends on prior publication

| Cache history | Reference situation at replay |
|---|---|
| Newly pressed note was unselected and never published | Its initial pop reference can remain available for its first publication. A raw copy can transfer that reference. |
| Fresh event allocation failed before publication | The cached pointer and initial reference remain. A later first publication may also transfer that reference. |
| Note was already published and its queued event completed | The queue's reference was released. The cached pointer remains, but no new reference is added for replay. Another owner or a proven lifetime rule is needed. |

This refines the previous audit: the cache cannot be treated uniformly as either owning or borrowed. A first transfer from an unpublished cache differs from a later replay of a previously published cache. No state marker distinguishing those cases was recovered in this path.

For lowest/highest selection, a newly pressed unselected note returns through `400efb8a -> 400efc44` **after** its record was allocated and cached. If that note departs before its first publication, the note-off descriptor overwrites its cached pointer with zero. No release for that discarded record was recovered in the inspected local path. That is a possible orphaned-reference case, not proof that no other system owner/cleanup exists.

For a previously published note, disabling arp provides a useful constructed ownership test: ordinary event completion can reduce the record reference to zero while the cache still contains its address. Subsequent raw replay then lacks an owning reference. The PC model exposes this mismatch; it does not demonstrate the exact trace on hardware or model all record reuse between those operations.

## Event-allocation failures

`400f0626` explicitly returns zero when the fixed event free-list head is null. It does not allocate or release payload records.

| Failure branch | Local outcome |
|---|---|
| `400efc1a -> 400efc44` | Common fresh/current-note event allocation failed. Nothing is published from this allocation; the cache was already updated. |
| `400efbc8 -> 400efc44` | First event allocation in a changed-selection note-off failed. No departing/replacement event is published by that branch. |
| `400efbf2 -> 400efc44` | The departing event was already copied and published at `400efbe4`; allocation of the remaining-note replay failed. There is no replacement publication or rollback in this local path. |

The active-note list and selected index are updated before these exits. The builder supplies no recovered success/failure ownership protocol to `400dc432`: after `400dc68e`, that caller performs stack cleanup and bookkeeping without testing a publication result or explicitly releasing descriptor `+28`.

A failed allocation does not immediately prove a leak, because the cache may still hold the record for a later first transfer. Failure followed by departure is the sharper case: the cached pointer can be discarded while the initial reference remains positive. Event-pool exhaustion frequency and all external cleanup remain unverified.

## Validation and next consequence

- Twelve confirmed-entry local control-flow graphs cover 755 instructions, including both setting setters, the selected-step setter/update/disable routines, the live-note producer, cache builder, event allocator, and direct MIDI route.
- Twenty-five byte anchors match the decoded stock image.
- Thirty-six PC specification checks cover thirteen recorded ownership scenarios, replay modes 2/3 with all selectors, unselected-note transfer/departure, fresh/replay allocation failures, the −1 gate, and ordinary modes 0/1.
- Both firmware hashes remain unchanged. No patched or flashable image was produced.

These are instruction-validated branch and ownership specifications, not a ColdFire emulator. Direct-reference inventories and absence of explicit local calls do not exclude computed aliases or hidden cleanup elsewhere.

For the V1 design, cached replay with non-null `+38` must be treated as possible. Do not add an unconditional retain/release change to stock payloads: doing so would mis-handle first-transfer cases. The next discriminating check is a faithful execution/reuse trace of the payload pool, cached slots, event completion, and retained templates under the persistent selected-step state, including the partial-publication exits. Until then, the separate owned trailer remains a storage proposal rather than a certified firmware implementation.
