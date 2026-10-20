# E11 — M1 synth-style arp programming

E11 adds synth-style step programming to the M1 MIDI arp: Left/Right select a
step, E changes its scale-degree offset, F sets length, and Up/Down enable/rest
the selected step. Root/scale and per-pattern storage are retained. M2-M4 arps
are not implemented. Open M1 FUNC + SYN2, then turn D clockwise for the step page.

The user reported E11 working on Digitone on 19 October 2026 and patterns saving
successfully on 20 October. This is user-reported operation; the installed hash
and every individual test were not independently verified. PC checks cover
native controls, pattern recall/mirroring, actual loader/startup, keyboard and
sequencer playback, 25 matching DIN/USB note pairs and modeled startup-DIN input.
Physical timing/cache, exhaustive project/reset behavior and guaranteed recovery
are not certified. Development is paused at the user's request.

## Download

Under **Assets**, download **Digitone-OS1.44-E11-patch.zip**, then extract it.
GitHub's automatic Source code ZIP/TAR downloads are not ready-to-use packages.
This release includes historical packages too:

| ZIP | Status |
| --- | --- |
| Digitone-OS1.44-E11-patch.zip | Current working M1 build; user-reported hardware operation and saving |
| Digitone-OS1.44-E09A-patch.zip | Earlier sequencer-owner correction; user-reported hardware operation |
| Digitone-OS1.44-E09-patch.zip | Historical preview; known M1 sequencer arp bug |
| Digitone-OS1.44-E08F-patch.zip | Historical baseline; known M1 sequencer arp bug |

## Create the firmware locally

1. Obtain your own official original Digitone / Digitone Keys **OS 1.44 SYX**.
2. Install Python **3.10 or newer** if needed; no extra packages are required.
3. Extract the E11 ZIP into a writable folder.
4. Double-click **Create Firmware.cmd** and supply the stock file path, or run
   `python apply_patch.py --stock "path/to/stock.syx"`.
5. The patcher checks both hashes, refuses overwrites and creates the E11 SYX.
   It never transmits MIDI/USB or installs firmware.

Only this original stock input is accepted:
`d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`.

Expected E11 output:
`d7d3776054093b8a9b2999fc5b100c4cb88d436ab62685b6cd44770a6e4ecf75`.

The ZIP contains a stock-dependent compressed XOR delta, patcher, launcher,
manifest, controls and recovery instructions. It contains no complete firmware,
private project/card, snapshot or recording. Delta packaging is not encryption
or a claim of redistribution permission for third-party content. No distribution
license has been selected for the original project contributions; see the repository License status.

Read **RECOVERY.md**, keep external project/sound backups and official stock
recovery available, and use a disposable project for a trial. These are
experimental changes for the original Digitone / Digitone Keys, not Digitone II.
The included SHA256SUMS.txt verifies ZIP integrity, not hardware safety.
