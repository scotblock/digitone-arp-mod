# Held-note arp setup, release, and scale context

Read-only static analysis of Digitone/Digitone Keys OS 1.42. Source firmware unchanged; no patched or flashable image created.

## Findings

The shared held-note path is now mapped through event construction, arp setup, and note release. It differs materially from sequencer input:

- Held-note events use setup priority 2; ordinary synth sequencer events use priority 1.
- An active higher-priority arp rejects lower-priority setup attempts.
- Another note at the same priority and with the same settings pointer normally joins the existing note list without replacing the arp identity or retained event.
- A changed settings pointer or higher incoming priority causes the existing note list to be cleared before insertion.
- Releasing the last arp note empties the active-note list; an ensuing accepted note can create a new arp identity.

These are instruction-level findings. Incoming MIDI Note On/Off convergence is now established in the follow-up below. Exact transport labels, configuration names, and all controller behavior still require confirmation; live hardware behavior has not been tested.

## Held-note event construction

Function `0x400dc432` accepts a track argument t and note argument n. It obtains index k from `0x40093b72`, which reads current-pattern-pointer +0x16119, then constructs:

```
B = 0x407b00cc + 0x1611d*k
T = B + 0x3d0*t
root_byte = T[0x3cb]
scale = signed_byte(T[0x3ce])
```

At `0x400dc4a6..0x400dc4b8`, a conditional branch calls scale membership with n and this root/scale. That branch depends on a note-to-track mapping at `0x41946f70`. Failed membership sets a suppression flag; later code at `0x400dc4ec` can skip event emission. This is an existing input filter, not scale snapping of each generated arp note.

This live-input path reads the canonical bank addressed by k. Do not assume it is always identical to the current backing pointer, particularly where that pointer could refer to an alternate copy. The canonical calculation itself is explicit.

The path fills a 0x30-byte input descriptor and calls `0x400efa20` at `0x400dc68e`. Synth tracks 0..3 are recognized by helper `0x4009e39e`; a separate branch handles MIDI tracks. The descriptor contains track, note, velocity, on/off state, flags, settings override, and parameter payload.

Builder `0x400efa20` writes a per-note event template at:

```
0x431d1758 + 0x2a18*t + 0x414 + 0x48*n
```

Key fields, at `0x400efa5a..0x400efa96`:

| Event field | Value |
|---|---|
| +0x0c | 2, setup priority |
| +0x04 | Input descriptor +0x0c; 1 for note-on, 2 for note-off |
| +0x08 | Input track t |
| +0x3c | Input track t |
| +0x14 | 1 note |
| +0x18 | Note byte |
| +0x2c | Null |
| +0x30 | Descriptor settings override, possibly null |
| +0x38 | Descriptor parameter payload |
| +0x28 | Flags |

The builder clones these 0x48-byte templates into scheduled events. It also maintains a per-track held-note bitmap and order list. Selectors `0x400ef810`, `0x400ef954`, and `0x400ef990` choose the most recently inserted, highest, or lowest held note in the traced branches. Settings +0x12a and +0x12e select relevant behavior; exact UI labels for these fields are not established here.

The settings used for selection can come from the override or fallback getter `0x4009c2f8`:

```
*(u32*)0x80003f54 + 0x18 + 0x146*t
```

That is companion/sound settings, distinct from T's root/scale.

## Keyboard and other input callers

The UI note route through `0x400388e4` calls `0x400dc432` at `0x4003898e`. Its upstream caller `0x40039394` reads the selected Track root and constructs the note before emitting it. Another UI note route calls the same builder at `0x400459c2`.

A configurable mapped-input path through `0x400df63c` also calls `0x400dc432` at `0x400df7da`; its table selects track and note mappings. These paths converge on the same held-note event construction.

The configurable mapped-input route is not the sole incoming MIDI path. The explicit MIDI status dispatch and direct channel-routing path are established in the follow-up below.

## Arp setup acceptance and replacement

The single direct caller of `0x4009719e` supplies these arguments at `0x4009dd80..0x4009dda6`:

```
setup(track, note_count, notes, duration, event_time,
      event_priority, settings_pointer, mode_output, reset_output)
```

The duration parameter can be zero; its broader role is beyond the acceptance gate described here.

Per-track arp state begins at `0x41344530 + 40*t`:

| State field | Meaning established here |
|---|---|
| +0x18 | Arp identity used to validate later ticks |
| +0x20 | Retained settings pointer |
| +0x24 | Retained setup priority |

Active state is tested through the non-null note-list head in `0x41345620[t]`.

At `0x400971b6..0x400971c4`, mode byte settings +0x10f equal to zero causes an immediate zero return and clears the mode output. This early exit alone does not prove that a previously active arp has been cleared.

At `0x400971e6..0x40097208`:

- incoming priority greater than stored priority marks a reset condition;
- incoming priority lower than stored priority is rejected when the note list is active;
- equal priority, or an inactive list, proceeds.

At `0x40097214..0x4009722a`, a different settings pointer or the higher-priority condition calls `0x400970b0` to clear the track's arp notes. A provided reset-output pointer is set to 1.

Insertion/reordering proceeds at `0x40097288..0x40097306`. Crucially, the local flag at stack +0x30 is set only when insertion encounters an empty note list. If that flag stays zero, `0x400973c8..0x400973cc` returns through the zero-result path without publishing new settings, priority, or identity.

When insertion starts an empty list, `0x400973d0..0x40097432` resets step/cycle state, stores settings and priority, advances the identity while skipping -1, and returns it. Playback then stores a copy of the initiating event for future arp ticks at `0x41345f08 + 0x48*t`.

Consequently, capturing V1 metadata on every note-on would not match existing context lifetime. Capture candidates should be attached to the accepted new arp identity, and rejected/additive events must not overwrite retained context by default.

## Note release

Note-off builder `0x400dc18a` writes a descriptor with on/off state 2 and invokes the same held-note builder for synth tracks.

Playback reaches `0x4009e2c2..0x4009e2d6`, which calls `0x4009743e(track, note)`. This removes the matching arp note from its linked list and bitmap and updates head/tail pointers. When the last note is removed, the list head becomes null, so active predicate `0x40097848` becomes false. A later arp tick then returns the existing negative/no-note sentinel.

The removal path does not itself zero the retained settings pointer, priority, or identity fields. V1 context therefore needs an active/identity validity rule; nonzero stored metadata alone cannot mean the arp is still active.

Explicit release/reset function `0x4009e3cc` also clears the held-note selection list through `0x400ef9f6`, and can clear arp notes depending on priority. Sustain-like deferral lists are visible in `0x400e1052` and `0x400e10d6`; their full controller routing remains unmapped.

## Pattern changes: what is proven and what remains

Mapped pattern-switch paths change current pattern/companion pointers and transpose configuration. The switch/reset helper `0x400ee6c4` does not itself clear the held-note state at `0x431d1758` or the arp note-list state. Those observations do not prove that every pattern-change mode preserves held notes; other callbacks or release events may intervene.

While a priority-2 held arp remains active, priority-1 sequencer setup is rejected. A subsequent held note can either join the existing arp, or reset it if playback now resolves a different settings pointer. A default settings lookup can change when the companion pointer changes; an explicit sound override may remain unchanged. Therefore 'pattern changed' alone is not a sufficient replacement rule.

For a source-context V1 policy:

1. Identify root/scale at held-note emission from the bank/index/track expression above.
2. Retain that candidate until playback setup.
3. Publish it only when setup returns an accepted new arp identity.
4. Keep it for additive notes at the same active identity.
5. Invalidate its use when the note list empties or the identity changes.

This is a proposed lifetime policy, not an implemented patch. It would keep a held arp's scale stable until an accepted new setup; switching it immediately to the new pattern's scale would be a different product behavior.

## Next bounded analysis

Identify the configuration setters for the special selected-track channel and the two incoming transport queues, and finish sustain/controller routing. Then build a PC-only context model covering rejected sequencer events, additive held notes, changed settings pointers, last-note release, pattern transitions, sound overrides, and later transpose. Do not choose RAM fields or binary patch sites before their layout/lifetime audit.

Source SHA-256 remains `0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`.

All conclusions are static. Targeted listings contain occasional data or truncated tails, which were excluded from the cited instruction chains.


## Follow-up: actual incoming MIDI convergence

Receive task `0x400db15a` registers input queues with low-level helper `0x400d9b68`, then handles two input queues at `0x400db1fa..0x400db2ae`. It reads the status byte, shifts it right four bits, and dispatches through the 16-entry function table at `0x401aade0`. The exact USB versus DIN labels for these two queues are not yet established.

The table proves these protocol identities:

| Status nibble | Handler |
|---|---|
| 8, MIDI Note Off | `0x400dc3e2` |
| 9, MIDI Note On | `0x400dc8c4` |
| B, Control Change | `0x400db68a` |

`0x400dc8c4` extracts channel from the status low nibble, note from byte 1, and velocity from byte 2. If velocity is zero, it branches to the Note Off handler. Otherwise it calls `0x400dc758(channel, note, velocity, source_flags)`.

Channel resolver `0x400dc758` compares the input channel to:

- `0x4131b9e4`, a special channel routed to selected track `0x4131b998`;
- each entry in the eight-track channel table at `0x4131b9e8`;
- `0x4131ba10`, another special channel routed through configurable mapping function `0x400df87a`.

The first behavior is consistent with Auto Channel, but that UI name is not confirmed by the traced setters. A matching ordinary channel can set multiple track bits when channels are shared. This means the receiving MIDI channel number must not be used directly as the track index.

For each resolved track, it selects canonical pattern bank B using current pattern index k, reads track fields +0x3cb root, +0x3ce scale, and +0x3cd, then calls related-note constructor `0x40106c30` at `0x400dc852`. It iterates up to four constructed notes, with -1 terminating the sequence, and calls held-note builder `0x400dc432` indirectly through a5 at `0x400dc898`. This closes the external MIDI-to-held-arp path that the earlier direct-call scan missed.

The source flags distinguish the two input paths and special-channel matches (8/16 on one queue, 2/4 on the other). Their interpretation as transport/source flags follows their construction, but the hardware transport labels remain to be verified.

Note Off handler `0x400dc3e2` calls `0x400dc2f6(channel, note, source_flags)`. That resolver uses track/channel state and retained generated-note bytes at `0x41945f50` to emit releases through `0x400dc18a`. On the special selected-track channel, it also consults the note-to-track map at `0x41946f70`, which allows a release to target its stored owner rather than blindly use the currently selected track. The configurable mapping channel has its own release route through `0x400df202`.

This gives V1 a stronger constraint: preserve original input-note and release mappings. Quantizing the arp's generated output is separate from changing the keys held in its note list. A release must continue to remove the corresponding stored input/generated note even if the sounding arp pitch was snapped elsewhere.

The known current/previous pattern switching and arp priority rules still apply. The mapped incoming Note On path uses the canonical bank selected at note reception; the active arp identity can outlive that reception context. Store V1 metadata only for an accepted new arp identity, rather than overwrite it for every arriving MIDI note.
