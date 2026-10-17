# E10 copy, clear, reset and unsaved working-cache checks

17 October 2026. Separate PC-only lifecycle image. E09A is unchanged; no installable E10 firmware is produced. See `Digitone-E10-PC-lifecycle-verification.json` for the result-gated summary.

## Changes

The earlier bank/editor connection exposed two real gaps: native pattern paste changed the MIDI kit without carrying its E10 record, and unsaved editor changes left the retained working image with an older record. Full named-project saves alone did not solve either gap.

The lifecycle adapters preserve the actual stock memcpy and kit encoder. Four verified function-pointer loads in the native pattern clipboard handlers are redirected to a wrapper; it handles only five recovered kit-copy continuations with the exact 0x988-byte copy size. It remembers a 32-byte record alongside each of three native clipboard/undo buffer identities and the current captured-project generation. Paste/undo resolves the exact destination project kit and updates its bank record. Unrecognized, missing or previous-generation clipboard data produces absent/disabled step settings. Cross-project E10 step paste is not implemented.

Accepted editor updates also synchronize the corresponding record in the fixed retained COKI working image. The incremental native kit serializer synchronizes only when both the source kit and serialized destination match the captured active project and its exact retained slot. Arbitrary encoder destinations receive no extra extension write. A capture revokes the previous binding; a matching full encode or retained capture establishes the current generation. The native COKI update helper invalidates and republishes its checksummed header. Header probing uses the pure native checksum routine, avoiding the stock validator's error-flag side effect on a rejected transient header.

The additional code starts at 0x47bf4000. Lifecycle metadata at 0x47bf6000 occupies 208 bytes, including three project-scoped clipboard sidecars. The native copier installs a 90,320-byte payload ending at 0x47bf60d0. These addresses are PC placements, not a claim of exclusive physical RAM ownership.

## Semantics and test scope

Full pattern paste/undo carries step settings with the native MIDI kit. Native trig clear retains arp settings, just as the observed stock MIDI settings do; undo-clear retains them too. Clearing trigs is therefore not a request to reset the arp program to defaults.

The continuous panel clipboard scenario starts from native cold startup and enters two distinct programs through the device editor in the same PC session. It performs an unsaved edit, copy, paste, undo-paste, paste again, clear and undo-clear, then another unsaved edit. Its independent native settings witness distinguishes completed paste from a queued button request. No bank, record, settings, hook or helper bytes are inserted by the runner. The retained image and bank are compared for all 128 slots and the native header checksum is checked.

Ten stopped reset-entry fixtures exercise diagnostic admission states, warm setup, pool wrapper/initializer, test exit and E10 cold-init refusal while LIVE. They watch the copied payload, legacy pool/header fields and the whole retained image. These are guarded-entry refusal checks, not proof of every factory reset, computed bypass, concurrent reset or later copier replay.

An explicit call to the existing stock retained-bank writer is followed by fresh native cold PC startup using the resulting private card. It tests whether the unsaved native editor records can be written and restored without Save Project. This explicitly supplied call frame is an execution fixture; automatic power-fail dispatch is not exercised. A passing result cannot establish real power-loss timing, available energy, incomplete-write recovery or physical persistence.

Named-project reload and keyboard/sequencer playback are separate regression workloads. The emulator's snapshot format omits EMAC mode; a checkpoint taken during fractional audio processing subsequently hit stock `GET_MACSR_MODE() == MACF_FRAC`. The revised load checkpoint waits for task-level interrupt state. No firmware assertion is bypassed or patched for this control.

## Recorded results

The consolidated verification report gates the following results: isolated native contracts and strict ColdFire decoding, cold copier/init, named load, the continuous native panel clipboard sequence, ten reset refusals, and 23 matched DIN/USB playback pairs. The unsaved panel session records +3 in A01 and +2 in A02 after undo/clear, with all 128 retained records equal to the RAM bank and a valid native COKI checksum. The explicit stock writer stores all 128 matching records, switches the retained bank and invalidates the old header. Fresh native cold PC startup restores all 128 matching records, including A01 +3 and A02 +2, without Save Project. The consolidated report passes.

## Remaining limits

Automatic physical power-fail recovery remains unverified. Physical RAM/DMA ownership, cache coherence and timing, packaged E10 loader continuity, asynchronous replacements, all reset/copy families, M2–M4, and cross-project step clipboard transfer remain separate work. No hardware-ready E10 claim is made.
