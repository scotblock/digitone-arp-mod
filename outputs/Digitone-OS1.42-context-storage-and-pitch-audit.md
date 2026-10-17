# Digitone OS 1.42: context storage and pitch insertion audit

Read-only static analysis, 2 October 2026. No firmware bytes were edited, repacked, or sent to a device. Addresses refer to the decoded main ColdFire image loaded at `0x40000400`.

## Outcome

The best candidate for **coarse arp-note quantization** is the valid-note fall-through at `0x4009df9a`, after the two existing transpose contributions and range check, before `d6` becomes fixed-point pitch. This preserves the existing note identity supplied to voice allocation. It is a candidate integration boundary, not a verified patch site.

**No safe existing storage location has been established.** The arp-state record has no unused word. Separate, explicitly owned context storage is the preferred design, but its RAM reservation and event-copy lifecycle still need proof. Unwritten bytes in one producer are not evidence of free storage.

An additional guard is needed if V1 is intended to suppress overflowing arp results: the firmware narrows positive arp results to a byte before the later transpose/range check. The current PC model specifies full-integer bounds and therefore does not reproduce this stock narrowing.

## 1. Arp-state storage is occupied

Each of four synth tracks uses a 40-byte record at `0x41344530 + 0x28 * track`.

| Offset | Observed use | Evidence |
|---|---|---|
| `+00` | Step counter | `4009759a–400975a8` |
| `+04` | Note-bitmap group traversal | `4009764e–40097658` |
| `+08` | Traversal direction | `4009773e`, `4009777a–4009779e` |
| `+0c` | Previously selected base note | `40097808`, `40097824` |
| `+10` | Remaining-note mask | `4009763c`, `4009769c–400976a0` |
| `+14` | Linked-note traversal cursor | `400975ee`, `40097612–40097620` |
| `+18` | Arp identity | `40097410–40097432`, `40097580` |
| `+1c` | Octave cycle | `40097600–4009760e`, `4009781c` |
| `+20` | Settings pointer | `400973fc`, `40097596` |
| `+24` | Accepted priority | `400971e0–40097200`, `4009740c` |

The four records end exactly at `0x413445d0`, which is the active-note bitmap base used by `40097244` and the clear routine `400970b0`. Enlarging the records in place would overwrite that bitmap and invalidate the hard-coded indexing. None of these fields can be borrowed for root/scale.

## 2. Event storage remains unproven

Playback events and retained per-track templates are 72 bytes (`0x48`), with retained templates at `0x41345f08 + 0x48 * track`.

The synth producer `40093c26` examines eight note slots (`40093d54`) and writes up to eight note bytes at `event+18` (`40093f08–40093f10`). Thus `+18..+1f` is note storage. In the traced synth producer, `+20..+27` has no observed initialization. **Those eight bytes are a candidate for further ownership analysis only, not approved scratch space.** Their interpretation across other event types, transforms, and consumers has not been exhaustively resolved. For example, another producer writes `+20` at `400942d8`; its complete type/consumer relationship remains to be established.

Other mapped fields already have live roles: type `+00`, on/off `+04`, playback track `+08`, priority `+0c`, velocity word `+10`, count `+14`, flags `+28`, settings `+2c/+30`, duration `+34`, reference-counted payload `+38`, source track `+3c`, arp identity `+40`, and list link `+44`. Unused flag bits and velocity padding are also unproven; no recommendation is made to reuse them.

The event allocator `400f0626` clears only `+44`, `+38`, `+30`, `+2c`, and `+00`. It does not initialize hypothetical context bytes. Its matching free routine `400f065c` recycles the address. Pointer-only context lookup would therefore risk returning metadata from a prior event unless allocation/free explicitly invalidates it.

### Copy paths that a separate context table must cover

| Path | Copy behavior | Consequence |
|---|---|---|
| Accepted initial arp, `4009de2a–4009de40` | `400f0690` copies into retained template | Commit accepted context and associate it with the retained template |
| Scheduled arp output, `4009ce38–4009ce3c` | Same helper copies retained template into pooled event | Propagate retained context, preserving identity |
| Track remap, `4009bd9e–4009bda6` | Direct `memcpy(0x48)` | A hook on `400f0690` alone misses this path |
| Held-note replacement, `400efbcc–400efbda` | Direct `memcpy(0x48)` from per-note template | Context must follow the selected held-note template |
| Pool allocation/free, `400f0626/400f065c` | Reuses event addresses | Clear stale associations on both lifecycle boundaries |
| Queue flush, `400f08f0–400f094a` | Frees queued events through `400f065c` | Invalidation must work for bulk flush as well as normal playback |

This is an observed set of paths, not an exhaustive list of all copies. Pool events, retained templates, and per-note held templates are different storage classes; a table indexed only by pool slot would not cover all three.

## 3. Context lifetime contract

Separate two pieces of information:

1. **Event candidate context:** root/scale captured from the explicit source pattern and source track when an event or held template is created. Keep values, not a pointer to mutable pattern storage. Queueing, template selection, copying, and remapping must preserve the intended source context.
2. **Accepted arp context:** a per-track snapshot committed only when setup creates an accepted new identity. Additive input and lower-priority rejection must not replace it.

Setup `4009719e` increments identity only when a new note list is seeded (`400972f0–400972fa`, `400973c8–40097432`). A zero return can represent a skipped or additive operation; it is not sufficient evidence of a new context. Commit on the actual identity-creation path, or a proven caller-side equivalent, rather than on every setup call.

A possible *logical* accepted-context record is eight bytes per track: 32-bit identity, root byte, signed scale byte, valid byte, and a reserved byte. Four such records require 32 bytes. This describes required data, **not a safe RAM address or a complete storage budget**: queued-event candidates and held-template candidates require additional storage, and firmware scale-index translation is still unresolved.

Use context only when all of these agree: valid record, synth-track bounds, active note-list head `41345620[track]`, state identity `state+18`, and event identity `event+40`. Require the arp flag `0x80000` as an additional gate; the flag alone is insufficient. Missing or mismatched context should leave stock pitch unchanged in the proposed integration.

Invalidate accepted context when the active list becomes empty, on explicit clear/reset, and at initialization. `400970b0` clears the head/tail, and startup/reset `4009713c` clears the lists and bitmaps but does not initialize a new context table. Ordinary release `4009743e` can empty the list without clearing identity or settings. Sustain-deferred note-off must retain context until the actual release reaches this list. Mode-off setup alone does not establish that the list was cleared.

Allocation, reuse, source remapping, identity wrap, and interrupted writes require an explicit lifecycle/concurrency design. Existing pool/list manipulation uses short interrupt-masked sections; a new context update must respect that execution model. No allocation or long scan should be introduced into the pitch path.

## 4. Pitch insertion boundary

| Address | Stock operation |
|---|---|
| `4009df78` | Unsigned event-note byte into `d1` |
| `4009df88–4009df90` | Compute note plus global transpose `80003fc4` plus per-track transpose from `800034c4` |
| `4009df94–4009df98` | Verify integer sum is in `0..127`; otherwise skip this note |
| **`4009df9a`** | **Candidate valid-note insertion boundary: change `d6` only** |
| `4009dfa4–4009dfa6` | Shift `d6` into 16.16 fixed-point form |
| `4009dfc8–4009dfcc` | Pass unchanged `d1` and track to voice allocation `4009e720` |
| `4009dfd2` | Save fixed-point pitch on stack |
| `4009e060–4009e066` | Store pitch baseline in `41345ebc[voice]` |

At the candidate boundary, `d6` is the valid transposed coarse note. Snap that value using the accepted context, leaving the event note byte and `d1` unchanged. `d1` is the stock untransposed event note used by voice allocation; for arp playback it is already the generated arp note, not necessarily the original physical key. Preserving it avoids redefining stock allocation/release matching. Physical held-key tracking also remains unchanged.

Do not quantize inside `40097818`: that location is before the later transpose additions and also updates the traversal state. Do not alter the held-key templates to implement output quantization. A future hook must preserve live registers, stack balance, and required processor state. Instruction relocation, branch reach, executable-space ownership, and exact calling convention have not been validated.

### Earlier narrowing needs a separate decision

The full arp result from `4009755e` is checked for negativity, then stored with `move.b` at `4009de98` for initial output and `4009df5e` for continuing output. Later `4009df78` reads that byte unsigned. A nonnegative result of 274 would become 18 before transpose; the later range check cannot recover the original overflow. This is a static arithmetic consequence, not a hardware observation.

If V1 should suppress such full-width overflows, add a separately validated bound check before **both** byte stores. Preserve negative-result handling, and still perform the existing after-transpose check. This is an additional behavior change beyond inserting a snap at `4009df9a`. The PC model already proposes full-integer bounds, so it must not be described as reproducing stock overflow behavior.

### Later pitch processing remains outside this guarantee

At `4009d550–4009d568`, a signed per-voice byte at `owner + 0x5f8 + 0x94*voice` is shifted into integer fixed-point units and added to the baseline before `400f02b4`. Its musical/UI meaning and writers are not yet established. A further contribution involving `+5f7` is added at `4009d580–4009d592`; `400f02b4` itself maintains pitch state and contains optional rounding.

Therefore this candidate locks the **coarse baseline after the two identified transpose contributions**. It does not prove final sounding pitch stays in scale under all later tuning, glide, bend, or modulation. Moving quantization downstream would require reliable voice-context ownership and a decision about whether those musical controls should remain expressive.

## 5. Safest next investigation

Finish the ownership trace for `event+20..+27` across every relevant producer, consumer, copy, and remap. In parallel within the same static investigation, map event-pool initialization and RAM/heap/stack boundaries to determine whether an explicitly reserved context table is feasible. A zero-filled region alone is insufficient proof.

Then resolve raw track scale values into the membership-table index, and trace the writers of the later `+5f8` pitch contribution. These checks decide storage, source-context propagation, and the precise musical promise of V1 before any patch design.

The existing PC model's ten scenarios and 4,608 scale cases were rerun successfully. They validate the proposed behavioral rules, not firmware storage safety or hardware operation. Firmware and the decoded executable were hash-checked against the prior inspection.
