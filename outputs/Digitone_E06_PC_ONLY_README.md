# Digitone 1.44 E06 — scale-degree arp candidate

File: `Digitone_OS1.44E06_SCALE_DEGREE_ARP_PC_ONLY.syx`

SHA-256: `9677c2434429016b1861ebcbb5cfbefcaa0a863c076e123acd84abf120a068d3`

This is a separate PC-tested candidate for Digiemu. E05 and the stock recovery firmware remain unchanged. E06 has not been installed on physical hardware. The version display remains 1.44; use the filename and checksum to distinguish builds.

## Musical behavior

Offsets count notes in the retained selected scale, starting from the selected held note. In C major, held C and offsets 0,1,2,3,4,5,6,7 produce C,D,E,F,G,A,B,C. Offsets -1,-2,-3 from C produce B,A,G below C. Seven degrees spans an octave for a seven-note scale; a five-note scale spans its octave in five degrees.

An off-scale held note is first anchored using E05's nearest-note calculation, with lower notes winning ties. Chromatic, invalid or unavailable context keeps the original chromatic arithmetic. Existing arp octave range, global/track transposes and E05's final scale constraint remain in place. Extreme results outside the stock unsigned-byte storage range cancel before truncation; the stock MIDI-range check still runs later. Existing patterns containing arp offsets will sound different with a scale selected.

## Changes and inherited protections

The actual arp step byte is read at 0x40098116. E06 changes that tail calculation; it does not reinterpret the later global/track transpose values as scale degrees. Only this eight-byte stock hook and three previously zero payload intervals change from E05. The copied payload remains 18,436 bytes. No new persistent RAM allocation, metadata layout or startup hook is introduced.

E05's corrected ColdFire startup instructions, native copying and initialization, root/scale capture, atomic context copying, cold/LIVE admission, input/release/sustain guards, deferred release cleanup and reset/UI refusal controls are retained byte for byte outside the declared new intervals. Diagnostic/test-mode entry remains unsupported as in E05. Added code and its lookup table are checked after native copying and again after playback.

## PC verification

- 322,735 arithmetic cases across all 35 scales, including the full signed-byte offset range at boundary notes, matched an independent oracle.
- 420 native tail-hook cases passed across four tracks, multiple interrupt masks, valid/chromatic/unready/bad-header/identity-mismatch contexts. Other registers and stack match the stock tail; monitored metadata is unchanged.
- Five startup cases passed: fresh/restored stock and candidate, plus disabled-feature fallback. Candidate copying is native; helper bytes were not host-loaded.
- Nine stopped-state diagnostic/reset refusal controls passed.
- Five continuous playback cases completed with actual DSP execution, MIDI delivery, sustain/release, pattern replacement and fresh notes. 48 observed scale-degree returns matched the oracle; the C-major eight-step workload reached every offset 0..7 through the native selector.
- Ordinary pitch sequences matched stock with chromatic context and with the optional feature disabled. Audio byte equality is reported separately and remains incomplete.
- Transport framing/sequence/checksums, container padding/checksum, compressed MAIN checksum, independent decompression and unchanged non-MAIN sections passed.

The playback test applies disclosed root/scale, input-gate and eight-step arp-setting fixtures before the native selector. It does not prove that every possible UI/project input reaches the same state. Clock/cache/DMA behavior is modeled and cannot certify physical deadlines or region ownership.

## First emulator test

Add E06 as a separate Digiemu firmware entry, leaving stock and E05 available. Start from a fresh session or a copy of a saved session. Select C major/Ionian, hold C, use a one-octave arp with offsets 0..7, and check for C D E F G A B C. Then try -1,-2,-3, a different root and a five-note scale. Test release/sustain and changing patterns. With scale off, compare chromatic behavior against E05. Keep E05 on the physical Digitone while checking this candidate.

## Remaining limits

E05's user-reported physical boot and C-major scale-lock result support that build only. E06 needs its own hardware trial decision; no physical installation was performed here. Exclusive RAM ownership, physical cache/DMA/audio timing, and unknown shutdown/interior reset bypasses remain inherited limitations. The earlier E04 logo hang is not a reason to claim that an emulator pass guarantees a physical boot.

## Evidence

- [Digitone-E06-PC-candidate-layout.json](./outputs/Digitone-E06-PC-candidate-layout.json)
- [Digitone-E06-degree-contracts.json](./outputs/Digitone-E06-degree-contracts.json)
- [Digitone-E06-boundaries-and-preservation.json](./outputs/Digitone-E06-boundaries-and-preservation.json)
- [Digitone-E06-PC-container-verification.json](./outputs/Digitone-E06-PC-container-verification.json)
- [Digitone-E06-PC-startup-comparison.json](./outputs/Digitone-E06-PC-startup-comparison.json)
- [Digitone-E06-PC-diagnostic-reset-controls.json](./outputs/Digitone-E06-PC-diagnostic-reset-controls.json)
- [Digitone-E06-PC-playback-comparison.json](./outputs/Digitone-E06-PC-playback-comparison.json)
- [Digitone-E06-arp-offset-provenance.json](./outputs/Digitone-E06-arp-offset-provenance.json)
