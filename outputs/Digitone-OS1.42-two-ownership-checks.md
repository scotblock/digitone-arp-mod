# Digitone OS 1.42: raw-copy ownership and retained-template reset checks

The requested checks have been run. The fresh live-note handoff and template replacement are now traced more precisely. Generic cached replay ownership and safe pool reinitialization remain unproved; neither is certified by an empty queue. Firmware is unchanged.

## 1. Raw event copies

### Fresh live-note handoff

The synth branch of `400dc432` clears a 48-byte stack descriptor. When parameter data is needed, `400dc5c8` obtains a record from the 64-record pool. `400dc5e8` stores that pointer at `a6-8`, which is descriptor offset `+28` relative to `a6-30`. `400dc68e` passes this descriptor to `400efa20`.

`400efa90` copies descriptor `+28` to cached event `+38`. The cache is located at:

`431d1758 + track*2a18 + 414 + note_slot*48`

`400efab8` clears the event's **32-bit type** to zero. The selected cache is then copied to a newly allocated 72-byte event at `400efc2a` and published through `400f0886`. Publication adds no payload reference. Thus a successful, single fresh-note publication can transfer the record's initial reference to the queued event; the cache itself has no separately retained reference on this path.

The note-off descriptor route at `400dc21c..400dc25a` clears its descriptor and sets `+0c` to 2. Its `+28` is zero. The corresponding current-slot cache overwrite therefore clears that slot's payload pointer before a current-slot copy.

### The remaining cached replay question is specific

In the note-selection branch, releasing one note may select a different cached note. `400efc08` copies the **selected other slot**, while `400efbe0` can copy the departing slot first. The other slot's `+38` is not cleared by the departing note's descriptor. Neither raw copy adds a payload reference.

The selector helpers `400ef810`, `400ef954`, and `400ef990` read the active-note list/bitmaps. The removal helper `400ef8b2` updates that list and its bitmaps. These inspected helpers do not retain/release payload records. The local producer also has paths that abandon publication when event allocation fails or a newly pressed note is not the selected note; a complete caller-side record disposal contract has not been established for those paths.

**What this proves:** a raw copy is not interchangeable with the common owning-copy helper. The fresh transfer case has a clear reference source. Replaying a different cached record needs an additional lifetime/eligibility contract.

**What this does not prove:** a stock-firmware use-after-free or reference-count defect. In particular, the runtime settings and ordering that permit a non-null payload in a replayed cache are not yet fully established. The PC counterexample described below is conditional, not an observed device failure.

## 2. Retained templates and reset

The four retained arp templates are at `41345f08 + track*48`.

| Operation | Recovered behavior |
|---|---|
| Capture/replace template, `4009de40` | Calls `400f0690`: releases the destination's old type-zero payload, retains the source's type-zero payload, then copies 72 bytes. |
| Generate queued event from template, `4009ce3c` | Uses that same helper, adding a reference for the new queued owner. |
| Ordinary event completion, `4009cef6` | Calls `400f065c`, releasing a type-zero payload and recycling the fixed event. |
| Queue drain, `400f08f0` | Detaches and releases queued events and scheduling nodes; it does not traverse the retained-template array. |
| Arp global reset, `4009713c` | Clears activity flags and note arrays; its confirmed local body has no calls and no template accesses. |
| Arp track reset, `400970b0` | Clears note activity and track flags; no retained-template cleanup was recovered in this path. |
| Cache global/track reset, `400ef9d0` / `400ef9f6` | Clears the selected-note list head and four bitmap words per track. It does not clear cached 72-byte events or release their payload pointers. |

Template replacement therefore supplies a known **old-record release**. Stopping arp activity does not establish release of every retained template. After queue drain, a template can remain the sole owning reference.

One inspected caller, `40094508`, masks interrupts at `40094518`, calls the queue/reset wrapper at `40094556`, and restores the saved status register at `40094562`. This supplies local interrupt exclusion around that call. It does not supply missing template cleanup or certify every other producer/task as quiescent.

The aligned literal search over `41345ee8..41346028` found template-base references only at the two common-copy call preparations, and template `+40` references used by arp scheduling. This is supporting discovery evidence, not proof that computed aliases or broad clears cannot exist elsewhere.

### Safe storage implication

The proposed 16-byte trailer belongs to the enclosing persistent allocation, not to any individual payload record. Record release does not free that enclosing allocation. Keep the trailer tied to the pool owner pointer `4199d590`; never derive its location from an arbitrary cached/template payload pointer, which may come from a separate auxiliary allocation.

Do not treat stop, queue drain, or zero arp activity as permission to rebuild the pool or clear the trailer. A new reinitialization protocol would need stopped producers, no active capture/update, disposal of all owning templates and queued events, and invalidation of any cache that could replay an old pointer. That protocol is a design requirement, not a recovered stock implementation. Calling the ordinary event-release helper on a static template would also be wrong: it recycles the event object itself.

The safest continued design is cold initialization of the owned trailer, with no added reset on ordinary stop or pattern changes. The second existing initializer route still needs its actual runtime reachability/usage established before a firmware implementation is considered ready.

## Verification

Six confirmed-entry local control-flow graphs cover 262 instructions. All decoded paths were checked without relying on misaligned window output; unsupported two-byte address-register test instructions were handled explicitly. Twenty-three byte anchors match the decoded stock image.

Eleven executable PC ownership checks cover fresh transfer, template capture/replacement, four-track queue drain, explicit template cleanup, and same-record replay. A conditional replay without a retain fails owner accounting and can leave a live record on the free list after destination replacement. Adding the required source retain balances that constructed scenario. These checks specify ownership rules; they do not emulate firmware or prove the failing trace reachable.

The original SysEx and decoded section 3 retain their previous SHA-256 hashes. No firmware bytes were changed and no flashable output was produced.

Next investigation: establish the actual eligibility of cached replay with non-null `+38`, including unselected-note and event-allocation failure paths. This is the concrete remaining ownership question; broader assertions of storage safety would be premature.
