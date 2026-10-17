# Live arp track context and pattern changes

Read-only static analysis of Digitone/Digitone Keys OS 1.42. No modified or flashable firmware produced.

## Result

The identified stock arp calculation does **not consume root/scale**. Its output is the chosen note plus octave-cycle and signed arp-step offsets. Therefore there is no existing scale-owning Track lookup inside that calculation to reuse unchanged.

For synth sequencer notes, the source track and its root/scale are now mapped exactly **at event creation**. Across pattern transitions, the event's source pattern can be the previous pattern rather than the current global pattern. A V1 implementation should preserve that event context rather than assume the global current pointer identifies its owner.

The correct metadata for a source-pattern policy is:

```
t = sequencer source track index
B = pattern backing pointer actually passed to event builder
T = B + 0x3d0*t
root_byte = T[0x3cb]
scale = signed_byte(T[0x3ce])
```

For synth sequencer generation, t is 0..3. This is the same underlying data used by the Track root/scale getters previously mapped through object +0x10. Root-byte extension and scale -1 require care; the getter uses a byte for root and explicitly sign-extends scale.

## Evidence: track index reaches the arp unchanged

The scheduler distinguishes synth tracks 0..3 from the remaining tracks at `0x40095202..0x40095206` and calls synth event builder `0x40093c26` with:

1. source track t;
2. source pattern B;
3. companion settings pointer K;
4. step index;
5. optional event object;
6. optional timing-result pointer.

The builder loads t into d4 and B into a3 at `0x40093c30..0x40093c42`. It reads note data using the 0x3d0 track stride. At `0x40093ef4` it stores t in event +0x08, and at `0x40093ef8` also in event +0x3c.

Playback dispatcher `0x4009ce78..0x4009ce8a` loads event +0x08 into d2 before taking the live-note processing branch. Arp setup at `0x4009dda2..0x4009dda6` receives event +0x08 as its first argument. Both calls to arp calculation `0x4009755e`, at `0x4009de8c` and `0x4009df52`, likewise receive event +0x08.

The arp selects its state as `0x41344530 + 40*t`, and reads its retained settings pointer at state +0x20. This closes the earlier uncertainty between the sequencer source track and the arp channel for ordinary synth sequencer events.

## Evidence: current and previous patterns coexist

The global pointer roles below are descriptive names inferred from their data flow, rather than recovered symbols:

| Address | Observed role |
|---|---|
| `0x41342150` | Current pattern backing pointer |
| `0x41342154` | Pending/candidate pattern pointer |
| `0x41342158` | Previous pattern pointer retained during transitions |
| `0x4134215c` | Current companion settings pointer |
| `0x41342160` | Pending companion settings pointer |
| `0x41342164` | Previous companion settings pointer |

Initial/context binding function `0x4009461c` assigns its first two arguments to current pattern and companion settings at `0x4009464c..0x40094652`. It also reads pattern-level and track-level transpose fields into playback configuration.

Switch path `0x400955e2..0x40095610` first copies current pointers into previous pointers, then promotes the pending pair when the pending pattern pointer is non-null. Another switch path at `0x400958fa..0x4009593e` similarly retains the previous pair and promotes the pending pair. A scheduled path at `0x40094d1e..0x40094d64` also replaces current state while retaining the former pattern pointer. These are multiple observed switch paths; their exact user-visible modes and scheduling rules are not fully named.

Most importantly, event scheduling at `0x400951bc..0x400951e4` explicitly chooses:

- previous pattern/settings at `0x400951ca..0x400951d0` when the per-track signed state byte is positive;
- current pattern/settings at `0x400951d8..0x400951de` otherwise.

It then passes the selected pair to the event builder at `0x4009524a..0x40095250`. The signed byte comes from the per-track array starting at `0x413421b4`. This proves that event provenance cannot always be replaced by the current global pointer. The precise relationship of this branch to microtiming and individual transition modes remains to be established; the old/new selection itself is explicit.

There are also per-track pattern pointer caches at `0x419a302c`, `0x419a2fe8`, and `0x419a3008`. The scheduler updates/copies them at track boundaries. They corroborate retained track-specific pattern context, but their timing relative to queued playback events has not been proven safe for a patch-time lookup.

## Evidence: ongoing arp steps reuse the initiating event

At `0x4009de12..0x4009de40`, playback marks the event for subsequent arp processing, stores its identity at event +0x40, and copies the entire 0x48-byte event to:

```
0x41345f08 + 0x48*t
```

The copy helper is `0x400f0690`. It handles a referenced parameter payload and copies all 0x48 bytes.

The type-6 arp tick path at `0x4009cd16..0x4009ce76` checks the channel's active arp state/identity, copies that retained event into a new event, adjusts its note length, and inserts it into playback. The retained event therefore carries its original track and settings selection into later arp steps.

However, the mapped event fields do not expose a verified unique source-pattern pointer:

- +0x08: playback track/channel;
- +0x2c: selected arp/settings pointer;
- +0x30: optional override, initially cleared by the allocator;
- +0x38: referenced parameter payload, not a proven source-pattern owner;
- +0x3c: original source track in the mapped sequencer builder;
- +0x40: arp event identity;
- +0x44: event-list link.

The builder selects +0x2c from `K + 0x18 + 0x146*t`, or from a sound/settings pool at `0x41311402 + 0x146*sound_index`. That pointer does not uniquely identify a pattern's root/scale. A sound override must not silently substitute for pattern scale metadata.

Do not treat the absence of a verified pattern field as proof that no indirect recovery is possible. It establishes that the mapped fields alone do not yet supply a reliable lookup.

## Remapping and live-input boundary

Helper `0x4009bd8a` copies an event, clears its settings/payload pointers, changes event +0x08 to a supplied destination, and saves the source +0x08 into event +0x3c. Thus source track and playback destination are not universally interchangeable. A V1 policy must say whether remapped notes use the generating track's scale or the destination's scale.

An additional note-processing path near `0x400efb32..0x400efc3e` clones per-track event templates. Its full input provenance and pattern-transition behavior have not yet been mapped. The exact sequencer result above must not be presented as complete coverage of held keyboard notes or external MIDI input.

## Safest V1 design direction

For a source-pattern policy, capture root and scale from B and t when creating a synth sequencer event, while the source pair is explicit. Carry that metadata into the retained arp event/state when setup actually accepts the initiating event, alongside its identity. Subsequent arp steps should use the captured context until a new initiating event replaces it. This is a design proposal, not an implemented or verified patch.

Do not write into apparently unused fields or expand the 0x48-byte event/40-byte arp state without auditing their layouts, allocation, and all copy/reset paths. A separately managed context would also require a lifetime and identity audit. Snapshotting values avoids later reads through a stale pattern pointer, but means edits to root/scale during a held arp would take effect on retrigger; that behavior needs an explicit product decision.

Before binary patch work, the next bounded analysis should map the live-input event templates and the arp setup acceptance/replacement conditions, then produce a host-only behavior model covering:

- identical track numbers in two patterns with different roots/scales;
- events scheduled from the previous pattern after current state changes;
- ongoing arp ticks followed by a new initiating event;
- sound overrides and remapped destinations;
- disabled scale (-1), negative arp sentinels, and note bounds;
- snapping relative to the later transpose stage.

## Verification and limits

These findings use targeted ColdFire disassembly, call-argument tracking, and virtual-table/reference checks. Arbitrary-window misalignment, embedded data, and truncated tail operands were excluded from the cited chains. No hardware execution or complete decompilation has been performed.

The original source attachment SHA-256 is unchanged:

`0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda`
