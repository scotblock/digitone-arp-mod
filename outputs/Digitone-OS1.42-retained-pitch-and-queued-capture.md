# Digitone OS 1.42: retained pitch context and queued-note capture

**Subsequent provenance finding:** `Digitone-OS1.42-descriptor-producer-and-pattern-ownership.md` traces this descriptor to host-supplied USB stream control words assembled by `40003830`. The queued note fields do not establish an originating Digitone pattern; the separate callback word targets a no-op in this image. The upstream producer target at the end of this report is superseded by that finding.

Read-only follow-up. The traced control flow supports obtaining accepted context from the **playback track's retained template** at the coarse-pitch boundary. The delayed-note enqueue site is also located, but its incoming note items contain no pattern identifier or scale values. Capturing the receiving pattern at enqueue is feasible as a proposed policy; recovering an earlier originating pattern is not established. No firmware bytes or device state were changed.

## 1. Playback-track retained read

The shared synth dispatcher loads playback track `event+08` into `d2` at `4009ce7a`. Both observed arp-note paths pass that same event track to `4009755e`:

| Path | Selection and successful return | Convergence |
|---|---|---|
| Newly accepted arp | Identity written at `4009de1c`; retained copy at `4009de40`; selection call `4009de8c`; negative test `4009de94..4009de96` | Nonnegative result written to note byte at `4009de98`, count set to one, then ordinary pitch loop |
| Existing/continuing arp, including remapped copies | Selection call `4009df52` with event identity and playback track; negative test `4009df5a..4009df5c` | Nonnegative result written at `4009df5e`, count set to one, then `4009df0a` and pitch loop |

`4009755e` constructs state address `41344530 + 40*track`. It compares the supplied identity with state `+18` at `40097580`, then checks active-note head `41345620[track]` at `4009758e..40097592`. A mismatch or empty list returns -2 at `40097838`. Disabled/control cases can return -1; arithmetic can also produce a negative result. The callers skip note output for **any** negative return. Selection preserves caller registers `d2..d7/a2..a4`, including playback track `d2` and event pointer `a3`.

The ordinary note loop reads the allocation note into `d1` at `4009df78`. It adds global and channel transpose at `4009df8a` and `4009df90`, tests the result against its seven-bit equivalent at `4009df94..4009df98`, and reaches `4009df9a` with valid transposed coarse note in `d6`. At `4009dfa4..4009dfa6`, stock code converts that note to fixed point. Thus the existing candidate boundary remains **before `4009df9a`**, after transpose/range validation and before fixed-point conversion.

At this boundary the logical retained lookup is:

```
track = event[+08]                 # same value as d2 in the traced path
state = 0x41344530 + 40*track
retained = 0x41345f08 + 72*track
head = *(0x41345620 + 4*track)
```

The retained base/stride is directly constructed at `4009de2c..4009de38`, followed by copy helper `400f0690`. This copy occurs after accepted identity/arp flag are stored and before the initial note byte is replaced by generated output. It therefore retains the initiating event rather than its first generated note.

**This is a verified address/control-flow expression, not an existing stock root/scale read.** Stock firmware has no proposed context marker in these bytes. A new lookup would read metadata only after its producers, accepted binding and storage ownership are established.

## 2. Required guard and effect

The proposed retained-context guard requires:

1. A synth event of type 0 or 1, ordinary note-on state, playback track 0..3, and arp flag `0x80000`.
2. Proven nonnegative selection through one of the two traced arp-return paths for this event. The flag alone is not a general provenance proof. In the traced ordinary path, a negative return zeroes count and cannot reach the note-loop insertion point.
3. A nonempty active-note list, and agreement between event identity, state `+18`, and retained identity `+40`.
4. A retained synth event with its own playback track equal to the selected track, ordinary note-on state, and arp flag.
5. Valid proposed metadata, retained source-field agreement, and accepted playback binding equal to the selected track.

The incoming copied tick's source scale/binding need **not** agree with the retained destination context. A tick remapped from track 0 can legitimately select track 1's accepted arp when their identities coincide. Track 1's retained source snapshot is then authoritative. Its source could itself have been another remapped track; do not demand that source equals playback destination.

The hook changes only coarse `d6`. Preserve `d1`, the event note byte, source track, identity, settings, timing and release fields. The stock voice allocator at `4009dfcc` receives the original allocation note in `d1`; modifying it would redefine note ownership. Leave octave, bend and glide downstream as previously traced.

The full-width arp return is narrowed into a byte before this boundary. A full-width overflow guard, if desired, still belongs before narrowing at **both** return sites, separately from scale quantization. This audit does not remove that earlier limitation.

The proposed guard is tested as a logical read, not as injected machine code. Exact scratch storage, register preservation for a helper, interrupt consistency, reset ordering, identity wrap, and global ownership of event `+20..+27` remain open. The observed flag/count flow supports the boundary in these routes; an exhaustive proof of all incoming branches is still required before relying on it as the only provenance mechanism.

## 3. Delayed-note producer and queue layout

The queue consumer/constructor is part of `400efcb8`, called from the audio/update dispatcher at `4009cae4`. The earlier audit's `4009cae6` reference is the absolute address operand, not the start of the call instruction.

The caller obtains an input descriptor through `40003830` at `4009ca96`, with a deferred descriptor/time pair retained in globals `41345e60/41345e5c`. The queue handler recognizes descriptor tag `0xec` at `400efd00..400efd08`. Flag `0x10` enables note-item processing at `400efe5a..400efe68`; four-byte items begin at descriptor `+10`. These are protocol note items; their full origin and relationship to MIDI/keyboard or another producer have not been established here.

The enqueue block at **`400efe7e..400efee8`** removes a free node, populates it and links it into the pending queue. Its node layout is:

| Node offset | Writer | Content |
|---|---|---|
| `+00` | `400efedc..400efee8`, free/reclaim paths | Link pointer |
| `+04` | `400efe8e..400efe94` | Zero-extended note; low byte at `+07` |
| `+08` | `400efe98..400efea2` | Zero-extended velocity/on-off value |
| `+0c` | `400efea6..400efeac` | Track from upper four bits of packed item word |
| `+10` | `400efeb0..400efebc` | Due time: supplied time plus `41345ab0` plus lower twelve-bit item offset |

Tracks above 7 return the node to the free list at `400efec0..400efed4`. Tracks 4..7 are outside the proposed synth-scale capture scope.

Initialization at `400efc8c..400efcac` creates **64 nodes of 20 bytes**, spanning `431dbfb8..431dc4b8`. Every node word has a role. There is no spare eight-byte field or safe in-place record expansion demonstrated by this layout. Some upper bits are zeroed by these writers, but zero values do not prove those bits can be borrowed globally.

At due time, the constructor at `400eff9c..400efffa` reads node track, note and velocity, builds a one-note event, and emits it. It reads neither originating pattern nor root/scale. Nodes are reclaimed at `400f0014..400f002a`; the allocator failure path also reaches reclamation. Any proposed side storage would need initialization on allocation, cleanup on rejection and reclamation, handling of failed event allocation, and persistent association with that exact node instance.

## 4. Where capture can happen—and what is still unknown

For a **local enqueue-time policy**, the capture boundary is after the item track has been validated (the valid branch at `400efed6`) and before the completed node is linked into the pending list. At that point the node and its track are explicit. A proposed reader could snapshot the local active pattern's root/scale values into separately proven storage and later transfer them into the emitted event. It must not defer capture until `400eff9c`, because a pattern change can intervene.

The known pattern-storage layout is `T = B + 0x3d0*track`, root byte `T+3cb`, signed raw scale byte `T+3ce`. The active backing pointer is `41342150`; held input also has a distinct canonical-bank lookup using its current pattern index. **This queued protocol does not pass B or an index. Its correct generating-bank relationship is not established by the note-item fields.** Reading either backing source is therefore a proposed receiving-pattern policy, not proof of original sender context.

For a strict **original-generation policy**, capture must happen farther upstream, before the descriptor is delayed or sent, and context must travel with that particular note. Two histories with different roots/scales can produce identical note/velocity/track/time items. No late lookup can distinguish them. Locating the tag-`0xec` descriptor producer and its source pattern is the remaining concrete provenance target.

This also means the queue path must not be assumed equivalent to the separately traced held-template builder. Its priority and eventual event shape resemble live notes, but that resemblance does not prove common source ownership.

## 5. PC validation and unchanged firmware

`digitone_retained_pitch_checks.py` passes **10 new scenarios** covering distinct source/destination scales with coincident identities, both synth types, negative sentinels, invalid event/retained fields, missing or wrongly bound metadata, empty accepted state, unchanged allocation bytes, an enqueue snapshot across pattern change, and inability to infer different historical scales from identical queue items.

The route guard now additionally checks retained playback track, note-on state and arp flag. Its five routing scenarios still pass. The event-context suite passes 15 scenarios, 92,160 encoding cases and 64 corruption checks; the original behavior suite passes 10 scenarios and 4,608 quantization cases. These are specification tests, not firmware execution. Queue snapshot storage is deliberately hypothetical; no stock record or firmware image is enlarged or written.

Results are saved in `Digitone-retained-pitch-check-results.json` and the accompanying earlier result files. The scripts use only the Python standard library and the model/scale files beside them.

Original SysEx SHA-256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`; decoded section-3 remains `ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6`.

## Next target

Find the `0xec` note-descriptor producer and establish its pattern ownership before transmission/deferment. Then audit a concrete storage option across both that queue and type-0/type-1 event lifetimes, together with consistent retained commit/read/reset handling. The pitch boundary is better supported, but firmware patching remains premature.
