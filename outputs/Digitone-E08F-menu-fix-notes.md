# E08F menu correction — PC candidate

16 October 2026. For original Digitone / Digitone Keys OS 1.44. This is a Digiemu/PC candidate, not a hardware-certified release. No firmware has been transmitted to the Digitone.

## What changed

E08E replayed a stock page-selection instruction with the wrong offset: -14 instead of -20. Ordinary page buttons therefore selected pages six positions too far along. This explains the reported effects pages before any generated test project was loaded.

E08F restores the stock offset. It also limits custom page opening and marking to M1 with FUNC + SYN2. Bare SYN2 follows stock behavior. Synth arp pages and other MIDI tracks keep their stock routing. MODE, RATE and GATE remain on the custom M1 page.

Only the two menu helpers changed within the existing payload. Payload length, RAM state, arena, initialization, arp processing and Stop/release helpers are unchanged. E08E, E07 and stock recovery files remain preserved. The OS version display remains 1.44; identify this build by its filename and SHA-256.

## What passed on the PC

- 96 isolated routing cases and 96 marker cases across all eight selected tracks, six page buttons and both modifier states, including nonzero upper register bytes.
- Actual panel checks on M1, M2 and T1. All 18 normal menu bodies match stock; 15 full frames match exactly, with transient differences confined to the title/status strip in the other three frames in the shorter UI-only run.
- The M1 custom shortcut, M2's stock effects shortcut, synth arp opening, return to M1 Source and synth arp opening after closing the custom page.
- Independent SysEx framing, checksums, padding and exact MAIN decompression. Non-MAIN sections remain stock.
- Loader-derived MAIN entry, native copying/initialization and startup to the UI, followed by menu execution without host-loading the corrected helpers.
- The repeated live M1 panel/playback test, with balanced MIDI note-ons/note-offs, release, MODE/RATE/GATE edits and tempo changes.

The first attempted broad panel test failed because it entered the M1 shortcut while still in an effects page. A focused trace showed the modifier byte and corrected shortcut worked from normal MIDI pages. The final panel test establishes a normal page before each shortcut and checks return/re-entry explicitly. This distinction is retained; arbitrary starting-page shortcut behavior is not claimed.

## Try in Digiemu

Add Digitone_OS1.44E08F_M1_ARP_MENU_FIX_PC_ONLY.syx as a separate firmware entry. Confirm TRIG opens Trig Parameters, SYN1 opens MIDI Source, FLTR opens CC Value, AMP opens CC Select and LFO opens its LFO page on M1. Bare SYN2 follows the stock MIDI source-page behavior. Then try FUNC + SYN2 from an ordinary MIDI parameter page: it should open M1 MIDI ARP. Press NO, then SYN1 to return to MIDI Source. Check a synth track's normal arp page too.

M2–M4 arps are not implemented. The generated project's full settings persistence and sequenced MIDI chord playback gaps remain separate. This menu correction does not certify physical timing, cache coherence, exclusive RAM/DMA ownership or arbitrary reset/input overlap, and is not a request to flash the device.

SHA-256: `085ef1cae6d22878da74acf4a756dd9a22389971f211208e9bd67ff349e146f8`. Size: 1,610,016 bytes. Live test: 81 note-ons / 81 matched note-offs.
