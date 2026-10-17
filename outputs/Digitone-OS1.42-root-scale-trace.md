# Root/scale storage and note-output follow-up

Offline static analysis only; no firmware modification or flashable output.

## Root and scale inputs traced

The caller around `0x40039d2a..0x40039e3a` provides concrete evidence for these fields within an object returned by its storage virtual method:

| Field | Getter | Evidence |
|---|---|---|
| +0x3cb | 0x40032550 | Returns a byte, defaulting to 60 when storage is absent; caller sign-extends it into d3 and passes d3 as the membership routine's root/reference argument |
| +0x3ce | 0x40032816 | Returns a signed byte, defaulting to -1; caller passes it as the membership routine's scale argument |
| +0x3cf | 0x400328a8 | Returns a boolean-like result; affects caller branching, exact UI meaning unresolved |
| +0x3cd | 0x4003271c | Returns a signed byte; affects surrounding behaviour, exact parameter unresolved |

At `0x40039e32`, the caller pushes the scale value, then root/reference, then a candidate note calculated as root plus an offset, before calling membership function `0x40106b6c`. This confirms the inferred argument order using actual callers, rather than table shape alone.

Another caller at `0x400dc4aa..0x400dc4b8` independently reads signed bytes +0x3ce and +0x3cb and passes them with a note value to the same function. Thus the field interpretation has two separate uses supporting it.

These are **storage-relative offsets**, not fixed RAM addresses and not yet proven to be the same object that carries the arp fields. The object/track association must be established before combining them. The default root/reference 60 is consistent with a middle-C keyboard reference; whether it also encodes octave position matters when implementing a pitch-class constraint.

## Output helper: further evidence, not final synth pitch

The large helper at `0x4009e720` takes the earlier note value as its second argument, held initially in d2. Its code maintains note-indexed tables, channel state, voice bitmasks, and object records. At `0x4009ebcc` and `0x4009ebda`, it stores d2 into two byte fields of a selected record, alongside other arguments and a pointer.

This strengthens the interpretation of the helper as voice/note allocation and bookkeeping. It does **not** prove that these records contain the final audible pitch, or that d2 remains unchanged along every branch. No claimed final synth-note address is justified yet.

The prior caller's 0..127 check on a separately adjusted pitch and its passing of the earlier note remain distinct operations. Future tracing must determine where those adjustments are applied during record consumption or synth dispatch.

## Current milestone and next task

Established so far:

- live arp candidate computes selected note + octave displacement + signed step value;
- callers consume the result as note state;
- musical-scale membership routine and interval/degree tables are located;
- concrete root/reference and scale fields feed that membership routine.

Still required before designing a patch:

1. Map the root/scale storage object to the arp's active track/channel and verify index conversion, including -1 unrestricted mode.
2. Follow allocated note records into synth dispatch and establish final transposition.
3. Choose an arp-only constraint point that preserves negative/control returns, disabled steps, timing, duration, and note bounds.

No existing nearest-note snapping routine has been established. A small quantizer remains a possible design, but its placement and inputs are not yet validated.
