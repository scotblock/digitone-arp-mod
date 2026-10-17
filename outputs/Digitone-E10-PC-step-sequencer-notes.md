# E10 — M1 scale-degree step sequencer prototype

17 October 2026. This is executable native machine code and a working native panel editor in the PC engine, **not an installable E10 firmware release**. E09A and E09 firmware files remain unchanged.

## Behavior

The M1 arp has a separate 1–16-step offset sequence. Each offset counts notes of the chosen scale, matching the E06 degree helper. Off-scale held notes use the same nearest-note/lower-tie anchoring. Chromatic scale selection keeps chromatic arithmetic. Pitch results outside MIDI 0–127 are silent steps rather than byte wrapping.

Rests advance the sequence and chord selection at the existing tempo-linked rate without allocating a generated descriptor. The native arena busy check prevents a blocked step from advancing or overwriting an outstanding note. Fresh phrases and Stop reset the playback cursor. Turning the step sequencer off retains E09A's ordinary ascending arp.

The prototype explicitly configures its own root and scale. It does **not** claim to capture the MIDI keyboard page's native scale settings. The consuming pattern's M1 record is the playback owner, following E09A; note +0x28 and cached 0x419c5b14 remain parameter-lock lists and must not supply settings.

## Native editor controls

From the existing M1 arp controls, turn D clockwise to enter the step page. Existing main MODE/RATE/GATE controls are retained. On the step page:

| Encoder | Control |
| --- | --- |
| A | Root |
| B | Scale |
| C | Length, 1–16 |
| D counterclockwise | Return to main arp controls |
| E | Select step |
| F | Offset, −24 to +24 scale degrees |
| G | Rest on/off for the selected step |
| H | Step sequence on/off |

These controls have been executed through actual native panel/encoder handling in the PC engine. They are not available in the installed E09A image. Direct selection with the sixteen trig keys is not implemented.

## Observed checks

- Twelve native step-engine contract groups: C/D major, negative offsets, rests, wrap, clipping, chord selection, disabled/other-owner bypass, busy arena, Stop and phrase restart.
- Seventeen native publication groups: complete-block validation, root/scale/length/offset limits, owner refusal, COLD admission and interrupt/condition-flag restoration.
- Seven native editor groups: all controls, clamping, owner refusal and byte-for-byte preservation of stock MIDI/CC record storage.
- Continuous keyboard and sequencer playback with an explicit eight-step configuration: 24 matched note pairs on each port, seven rests and no clipped notes.
- Continuous playback after creating a four-step sequence through the native editor: offsets 0,1,2,3, step 3 resting, C Ionian. It produces C/D/F pitches, 23 matched pairs per port, seven rests and a reset cursor after Stop. The sequence values are not host-written in this final check.

The native code uses 448 bytes for the engine/cloned original helpers, 466 for atomic publication, and 2,164 for editor/rendering/cloned controls, plus 496 bytes of strings/tables and a 64-byte state. Prototype placement has gaps and is not a compact final loader layout. ColdFire decoding and the known MOVE restrictions passed for the new code.

## Remaining integration

All added executable bytes and initial state are loaded by the PC harness. The final panel check configures the sequence natively after that initialization. No updater, startup copier or native reset initialization includes the extension yet. The RAM interval is proposed PC-only storage; physical ownership/lifetime/cache/timing is not certified.

The prototype keeps one temporary owner-bound sequence. It does not provide durable per-pattern storage, project save/load, copy/paste, import/export or protection against every owner-pointer reuse. UI admission checks do not establish complete storage lifetime. M2–M4 are not implemented.

Existing MIDI records offer the two-byte MODE/RATE/GATE extension, insufficient for sixteen offsets, rest mask, length and explicit root/scale. A straightforward representation needs at least 21 saved bytes before version/integrity metadata (length can share an enable flag). Do not borrow stock CC fields, another track's settings or parameter-lock list memory. A separate owned saved representation and verified native serialization route are still required.

Next: establish per-pattern saved storage and copy/reset rules, compact/install the new code and initialize its state through startup, then repeat panel and playback checks from that packaged path. No full firmware candidate has been generated for E10.
