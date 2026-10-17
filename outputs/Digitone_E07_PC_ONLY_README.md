# E07 — synth arp to DIN MIDI, PC-only candidate

Firmware: `Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx`

SHA-256: `a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd`

E07 retains E06's scale-degree synth arps and mirrors generated arp notes through five-pin DIN MIDI OUT. This candidate is for Digiemu testing first. E07 has not run on physical hardware. E06, E05 and stock recovery files remain unchanged. The on-screen version still reads 1.44.

## Behavior

Each synth arp uses that synth track's configured MIDI channel (normally T1–T4 use channels 1–4). With a channel set to OFF, no new mirrored notes are emitted. The existing MIDI output selection must include MIDI/DIN; USB-only output does not enable this mirror. This version does not mirror over USB and does not add arps to the four independent MIDI tracks.

The emitted pitch is the accepted final synth pitch, including E06's scale-degree calculation and later stock transposes. Velocity comes from the synth note event. Note-offs follow observed native voice retirement paths, including ordinary gate expiry and allocator replacement. Shared/unison voices send one note-on per destination channel/note, then one note-off when the last mirrored voice retires. The note-off retains the original channel if settings change while a note is active.

When the native DIN ring is full, a new note-on is declined without claiming an external note. A blocked note-off remains pending and the stock MIDI task retries it. This handling passed isolated native controls; physical congestion timing remains unmeasured.

## Implementation and validation

The 1,176-byte helper set and 160-byte state table fit in previously zero padding within E06's existing 18,436-byte copied payload. The copier, payload length, source interval and reserved-RAM extent are unchanged. The native copier supplies both code and initial state; the final tests do not host-load the MIDI helpers or inject outgoing packets. E05/E06's startup, input, release/sustain and reset refusal protections remain in place.

- Five matched startup cases passed, including fresh/restored candidate startup and E06 feature fallback. The native-copy checks include the new helpers and state seed.
- Nine stopped-state diagnostic/reset refusal controls passed.
- Seventeen isolated MIDI controls passed, including all four configured channels, shared voices, original-destination release after channel change, inactive/invalid controls and output congestion. The isolated transport endpoint is a stub; continuous playback uses the real stock transmitter.
- Two continuous packaged sessions passed: mirroring enabled and a disclosed mirror-disabled control. The enabled run emitted 48 note-ons and 48 matching note-offs, dropped none, and ended with no active mirrored notes. Its MIDI notes include C D E F G A B C. Sustain, release, completed pattern replacement and fresh notes were exercised.
- The internal pitch sequence matches E06 and the mirror-disabled control. This does not establish audio byte equality or physical audio deadlines.
- Transport framing/checksums, compressed MAIN checksum, exact independent decompression and unchanged non-MAIN sections passed.

Continuous playback currently covers T1. Four simultaneous arps, mute/panic paths, rare reset/destruction routes, USB mirroring, physical queue timing and exclusive ownership of all newly used padding remain unverified. The selected RAM is within the old copied range; that fact is not an exclusive-ownership proof. Use separate destination channels for independent MIDI-track sequences: their channel/note ownership is not coordinated with the mirror table.

## First emulator test

Add E07 as a separate firmware entry and keep E06 available. Select a MIDI output or loopback port in Digiemu. In MIDI CONFIG → PORT CONFIG, set OUT PORT FUNC to MIDI and OUTPUT TO to MIDI or MIDI+USB. Use T1's configured synth MIDI channel as the receiver channel. For the first arp-only test, set TRIG KEY DEST to INT to avoid also transmitting raw keyboard notes. Record MIDI in Ableton and leave the recording track's MIDI output unassigned to avoid echoing notes back into the emulator.

Use C major/Ionian, a held C and offsets 0–7. Verify C D E F G A B C, then stop and inspect that every note has an end. Repeat release/sustain and pattern-change tests. In a later physical trial, the intended connection would be Digitone MIDI OUT to Rubix22 MIDI IN, with Rubix22 connected to the computer; E07's mirror does not use Digitone USB MIDI.

Do not install E07 on the physical Digitone as part of this PC test. No E07 hardware trial was performed or authorized here.

## Evidence

- [Digitone-E07-PC-candidate-layout.json](./outputs/Digitone-E07-PC-candidate-layout.json)
- [Digitone-E07-MIDI-contracts.json](./outputs/Digitone-E07-MIDI-contracts.json)
- [Digitone-E07-PC-startup-comparison.json](./outputs/Digitone-E07-PC-startup-comparison.json)
- [Digitone-E07-MIDI-native-playback.json](./outputs/Digitone-E07-MIDI-native-playback.json)
- [Digitone-E07-PC-container-verification.json](./outputs/Digitone-E07-PC-container-verification.json)
- [Digitone-E07-PC-diagnostic-reset-controls.json](./outputs/Digitone-E07-PC-diagnostic-reset-controls.json)
- [Digitone-synth-arp-MIDI-lifecycle.json](./outputs/Digitone-synth-arp-MIDI-lifecycle.json)
