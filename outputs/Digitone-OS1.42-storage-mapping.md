# Arp settings ownership and track-context mapping

Read-only static investigation; source firmware unchanged and no rebuilt image produced.

## Arp settings pointer: source and ownership

At `0x4009dd48..0x4009dd7a`, playback chooses its settings pointer in a5:

1. use note/event object field +0x30 when non-null;
2. otherwise use field +0x2c when non-null;
3. otherwise compute `*(u32*)0x80003f54 + 0x18 + 0x146 * d2`.

The alternatives suggest overridden settings versus a channel-indexed default block, but the exact meanings of fields +0x30/+0x2c and d2 are not yet named.

At `0x4009dda6`, the pointer is passed as the seventh argument to setup function `0x4009719e`. This matches that function's load at frame offset +0x58, accounting for its 0x3c-byte stack frame and the return address. At `0x400973fc`, setup stores it at **per-channel arp-state +0x20**. Pitch calculation `0x4009755e` subsequently loads exactly that field at `0x40097596`.

This is a concrete provenance chain from playback settings selection to the live arp's storage reads. At `0x4009de5a`, the same pointer is also retained in the table `0x41345ee8`, indexed by note/event object +0x08.

## Root/scale belongs to a different accessor path

In the scale-check UI caller, `0x400237b0` returns an object obtained through:

- a selected-bank/pattern-like calculation in `0x4002377a`: outer object +0x110c + 0x38c * clamped index (0..127);
- `0x400206b2`: returned object +0x70 + 0x58 * clamped track index (0..7).

The selected index comes through shared view/context helpers and still needs exact naming. The clamped track index comes from getter `0x40029a92`, which reads a storage word at +0x08. Root and scale getters are then called on this resulting track object.

By contrast, the arp UI obtains its settings object through `0x4001b16e`, which computes another object +0x60 + 0x328 * clamped index (0..3).

These **different strides and ownership paths** reinforce that arp settings and musical key/scale metadata must not be treated as one storage object. The four-entry arp UI path versus eight-entry root/scale track path also needs explicit handling of synth/MIDI track contexts. We have not yet derived a safe runtime expression for the appropriate root/scale object from the live arp channel.

Another root/scale caller uses a raw bank-based structure with 0x3d0-byte entries. This may represent backing storage, but its relationship to the accessor objects remains to be established.

## Note-record follow-up

Helper `0x4009f0f4` acts as a voice-release/bookkeeping routine: it reads a 20-byte-per-voice record under `0x80005434`, updates note/channel masks, and clears record bytes to -1. This supports the interpretation of the structures created by `0x4009e720` as allocation records rather than proof of final synth pitch.

Getter `0x4009f2a6` reads a signed byte at offset +2 from the same 20-byte record. A caller at `0x4009d2f4` uses that result to query note/channel masks and reconcile active voices. This path remains bookkeeping, not a located synth command.

The global adjustment `0x80003fc4` is set by function `0x4009c004` and by a configuration path at `0x4009cc14`. Nearby code initializes channel adjustments in a related table. Their final application to synth pitch remains unresolved; they must not be assumed to be the track root/scale settings.

## Outcome and next target

This stage establishes the complete arp-settings pointer chain and narrows why scale metadata cannot simply be read from it. It also distinguishes allocation/release records from synth dispatch.

The next investigation should follow the track object's storage virtual method to its backing bank and connect its selected track index with the playback channel, then identify consumption of the voice records by the synth/control layer. A patch design remains premature until that mapping and final pitch are established.
