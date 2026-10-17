# Musical scale utilities and downstream pitch trace

Continued offline, with no firmware alteration or rebuilding.

## Musical scale code located

Full scale-name table begins at `0x40200378`, with short names at `0x40200408`. Accessors `0x40106db2` and `0x40106da2` index those respective tables. Nearby utility code uses musical scale data, rather than sequencer timing scales.

**Membership candidate: 0x40106b6c**

- Takes three stack arguments, consistent with note, root/reference pitch, and scale index.
- Rejects note values outside 0..127 through an unsigned comparison.
- Scale index -1 accepts any in-range note.
- Reduces the note relative to the root by adding/subtracting octaves.
- Indexes a **13-byte-per-scale** table at **0x401b107c**.
- Returns 1 when the table byte is nonzero and 0 otherwise.

The handling of the octave endpoint allows a relative value of 12 as well as 0. Root-range assumptions and scale-index bounds must be checked at callers. This is a membership test, **not** a nearest-note quantizer.

**Degree-lookup candidate: 0x40106be2** uses the same table, returning its signed byte minus one. It is used by **0x40106c30**, a routine that writes a small group of related pitches to an output buffer. That routine uses a seven-byte-per-scale interval table at **0x401b0578**, with recognizable major intervals `0,2,4,5,7,9,11` followed by other modal interval sets. Its other branches and special scale cases need fuller interpretation before reuse.

This is concrete evidence that existing musical root/scale logic is present and readable. It does not establish the currently selected track's root and scale storage or prove that a ready-made snapping function exists.

The first membership row is `1,0,2,0,3,4,0,5,0,6,0,7,8`, consistent with major-scale membership and numbered degrees. The name table begins with CHROMATIC, whereas membership index -1 handles unrestricted notes. Therefore name-table and utility indices must not be assumed identical; their conversion needs verification at callers.

## Output path qualification

The arp-return callers save a nonnegative result in note-state byte +0x18. At `0x4009df78`, downstream code reads a note byte into d1, computes an adjusted value in d0 by adding a global value at `0x80003fc4` and a channel-indexed value from `0x800034c4`, and checks whether that sum lies in 0..127.

It then calls **0x4009e720**, passing the earlier d1 note as an argument, rather than the checked d0 sum. Consequently, the earlier description of this as straightforward final transposition was incomplete: the bound-check value and passed note differ. The helper begins with note/voice bookkeeping and many state tables; its complete pitch flow has not yet been recovered.

A constraint placed in the arp arithmetic alone might produce the wrong key after later adjustments. A constraint placed in a shared output helper might affect non-arp notes. Neither location is justified yet.

## Next concrete task

Trace the membership routine's callers to establish where root and scale indices come from, and continue the output helper far enough to identify the pitch actually sent to the synth. Then connect the selected track's scale state with an arp-only point in that flow. The initial implementation would still need a defined rounding rule and explicit preservation of negative return values, disabled steps, bounds, timing, and note duration.
