# Digitone OS 1.42: receiving-pattern capture timing and queue storage

**Follow-up correction:** [The byte-alias and pattern-writer audit](Digitone-OS1.42-byte-alias-and-pattern-writer-audit.md) found separated root/scale stores in group restore/reset paths. A reader-side interrupt mask alone cannot certify a consistent snapshot if capture preempts an already partially completed writer. The capture protection proposed below is therefore insufficient without writer-side transaction/ownership evidence. Queue storage remains compatible only within the traced paths.

The observed queue path supports a concrete receiving-pattern capture policy, and a compact storage candidate now avoids adding RAM or enlarging queue nodes. **Neither is certified for firmware implementation yet.** Capture should take one consistent view of the four synth tracks before processing a descriptor's note items. The candidate stores root/scale in the otherwise unconsumed upper three bytes of the queue note word, preserving the low note byte. No firmware was modified or rebuilt.

## Capture timing

The audio/update caller invokes the host descriptor handler at `4009cae4`, then obtains queued playback work at `4009cb66` and dispatches event types at `4009cb98`. Inside the descriptor handler, note insertion at `400efe7e..400efee8` precedes due-note conversion at `400eff42..400efffa`.

Consequently, this proposed policy captures the **receiving pattern when the completed descriptor is handled**, before the note enters the delayed queue. It does not capture USB arrival time, host generation time, or necessarily the pattern active when the event is later played. Deferred descriptors at `41345e60/41345e5c`, stream reassembly, and future due times can all separate those moments.

The receiving backing expression is:

```
B = *(0x41342150)             # load once for this snapshot
T = B + 0x3d0 * synth_track
root = unsigned_byte(T + 0x3cb)
raw_scale = signed_byte(T + 0x3ce)
```

Use the actual backing pointer B, not a later canonical-bank lookup from the pattern index. This is a proposed receiving-pattern rule; it does not recover the host's historical scale. Reject missing backing storage or invalid values rather than inventing a default source snapshot.

The active pointer can change through the following traced stores:

| Store | Meaning supported by adjacent code |
|---|---|
| `40094652` | Explicit pattern install from function argument, alongside companion settings pointer |
| `40094d64` | Pending-pattern transition, saving prior backing and companion pointers |
| `4009560a` | Boundary/start transition to pending backing |
| `40095926` | Another pending-pattern switch after saving previous backing |

These are observed stores, not a proof that no indirect writer exists. Queue capture occurs before ordinary event dispatch in the observed callback, but that order alone does not establish global ordering against main-task changes, higher-priority interrupts, or edits to pattern storage.

### Consistent descriptor snapshot

Capture one set of four root/scale pairs after confirming a valid `0xec` descriptor and its note flag `0x10`, before the loop starting at `400efe68`. Then populate all note nodes from that set. This avoids per-item reads of a changing active pointer and gives every synth note in the descriptor the same receiving-pattern view.

A bounded proposed critical section saves/restores the existing interrupt state, loads B once, copies eight bytes for the four synth tracks, and exits. It performs no allocation, callback or scan. CRC calculation, node population and queue linking occur afterward. This follows the short interrupt-mask style already used in the firmware; the exact interrupt/ownership proof and suitable insertion mechanics remain open.

The normal root setter `40032580` clamps to 0..115 and writes one byte at `400325c4`. The scale setter `40032846` clamps to -1..34 and writes one byte at `40032882`. Neither setter contains its own interrupt mask in the traced function. Their callers may provide protection; this audit does not claim those callers are unlocked. Holding B once prevents cross-pattern lookup mixing. Protecting the bounded read can prevent a writer from running between the reads, but cannot prevent capture of a writer transaction already paused between stores. The follow-up audit establishes this distinction; pattern copies and caller protection remain to be covered.

The handler currently reserves `0x1c` stack bytes, all occupied by saved `d2..d5/a2..a4`, and reads arguments at `+20/+24`. There is no existing eight-byte local reservation. A stack-based descriptor snapshot would require a deliberate frame expansion and adjustment of both argument offsets and the epilogue at `400f0034`. The complete handler's observed stack references were reviewed; no frame edit was made. Stack capacity and interrupt nesting are not established here.

## Queue ownership and compact storage

Nodes remain 20 bytes, 64 entries, at `431dbfb8..431dc4b8`. The traced payload uses are:

| Node bytes | Producer/consumer evidence | Assessment |
|---|---|---|
| `+00..+03` | Free/pending links, enqueue and reclamation | Fully owned |
| `+04..+06` | Zeroed by the full-word note store at `400efe94`; no read in the traced consumer | **Three-byte snapshot candidate** |
| `+07` | Low note byte read at `400effca` | Preserve exactly |
| `+08..+0b` | Velocity/on-off tested as a full word at `400effaa`, read/shifted at `400effda..400effe6` | Do not borrow upper bits |
| `+0c..+0f` | Track read as a full word for shifts and event track/source | Do not borrow upper bits |
| `+10..+13` | Full due-time arithmetic | Fully owned |

The input note writer is `mvz.b` followed by `move.l` at `400efe8e..400efe94`, so it currently initializes all four note-word bytes on each enqueue. Queue linking and reclamation touch `+00`, leaving the note word intact. No queue-node memcpy or node-pointer handoff to a payload consumer appears in the traced handler: emission passes a separately allocated event to `400f0886`. The held reset uses `431dbfb8` as an end boundary, not as queue payload.

These observations establish compatibility within the traced chain. A global alias/indirect-consumer audit is still needed before certifying the upper bytes unowned. The earlier conclusion that every node *word* has a role remains true; this proposal narrows ownership to byte granularity within the note word.

### Proposed three-byte encoding

This queue candidate needs only root and raw scale. Source track is already stored in the node; playback binding and arp identity do not exist until later accepted setup.

The upper three bytes of the note word hold:

- A 16-bit header: three-bit marker `101`, seven-bit root, six-bit `raw_scale + 1` (valid 0..35).
- An eight-bit CRC, polynomial `0x07`, over header, original note byte and synth track.

The low byte remains the original note. A missing/invalid capture, release event, or MIDI track writes the ordinary zero-extended note word, explicitly invalidating metadata. The marker/CRC identifies format and detects modeled corruption; it does not prove freshness. Freshness requires the full-word producer overwrite before publication on **every** enqueue path.

At due-note conversion, validate track 0..3, positive velocity, header bounds and CRC, then expand the snapshot into the previously proposed event context before emission. This transfer must occur while the node is still owned, before reclamation. Event `+20..+27` ownership remains a separate unresolved requirement; this audit does not certify that destination.

## Allocation, dropping and reset

| Case | Required behavior for the proposal |
|---|---|
| No free queue node | Preserve stock dropped-input behavior; no metadata allocation or side entry |
| Track above seven | Existing rejection returns the node; no published snapshot |
| MIDI track 4..7 | Keep stock note word and invalidate synth metadata |
| Release/zero velocity | Keep raw release identity; invalidate proposed scale candidate |
| Event allocation failure | Existing path reclaims the node; do not leave a separate snapshot owner |
| Successful emission | Copy decoded values to the event before unlink/reclaim; later reuse cannot alter that copy |
| Recycled node | Full note-word overwrite installs the new snapshot or clears it |

Initialization was traced through `4009bd08 -> 400f00ea -> 400efc56`, before audio callback address `4009c838` is installed at `4009bd52`. The initializer builds pending-list sentinels and links the pool through `+00`; it does not clear node payload words. Startup clearing and per-enqueue overwrite are therefore different mechanisms.

The initializer links nodes onto the existing free-list head without an explicit head clear. It must not be assumed safe to rerun against a live queue. No new queue-reset operation is proposed. Existing stop/sustain/held resets are not proof that this delayed queue is flushed. Pending snapshots should follow the stock node lifetime until emission, rejection or an actually traced flush; inventing a flush would change musical behavior.

Compared with a side table, the compact candidate avoids a global pointer, an extra RAM reservation, slot-generation bookkeeping and per-node allocation. It still requires byte-ownership proof and producer/consumer edits. Arbitrary cleared RAM, descriptor padding and managed heap allocations remain uncertified alternatives.

## PC checks and limits

`digitone_queue_snapshot_checks.py` passes ten specification scenarios, **18,432 root/scale/track encoding cases**, all 128 allocation notes, and 32 single-bit note-word mutation checks. It covers linking, context transfer before reuse, explicit invalidation for releases/MIDI/missing capture, a dropped-emission/reuse sequence, and one descriptor snapshot across a later pattern change. It also demonstrates why independent live field lookups can mix contexts.

The checks do not execute firmware or prove interrupt consistency, real pool ordering, timing, reset behavior, stack capacity, or global field ownership. Results are saved in `Digitone-queue-snapshot-check-results.json`. Only PC models and analysis documents were written.

Original SysEx SHA-256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`; decoded section-3 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.

## Remaining implementation gates

Close the upper-note-byte alias audit and pattern-writer/interrupt consistency, including in-place edits and pattern copies. Verify frame capacity and register preservation for the bounded descriptor snapshot. Then close event-context ownership and accepted retained commit/read/reset consistency. The compact queue encoding is now a reviewable PC-only design, not authorization or evidence for a flashable patch.
