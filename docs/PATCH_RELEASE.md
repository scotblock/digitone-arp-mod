# Stock-dependent OS 1.44 patch packages

Download the ZIP under **Assets**, then extract it. GitHub's automatic source-code downloads are not the ready-to-use patch packages.

| Package | Purpose | Evidence |
| --- | --- | --- |
| `Digitone-OS1.44-E08F-patch.zip` | Historical baseline with corrected menus | User-reported hardware operation; **known M1 sequencer arp bug** |
| `Digitone-OS1.44-E09-patch.zip` | E08F plus synth arp DIN/USB/both routing | PC-only routing preview; **known M1 sequencer arp bug** |
| `Digitone-OS1.44-E09A-patch.zip` | E09 plus corrected M1 sequencer settings ownership | **PC-tested correction; no new physical trial** |

No M2–M4 arps or MIDI arp step editor are included. Sequenced MIDI chord handling and saved-project persistence remain incomplete investigations.

E08F/E09 incorrectly treat a sequencer parameter-lock list as a full settings record, which can turn the arp OFF. E09A reads the M1 record belonging to the consumed pattern context instead. A panel-entered sequence reproduces the old failure; E09A retains the arp and produces repeated pulses, with live keyboard coverage and matched DIN/USB notes. Multi-note sequenced chord output is additionally covered by isolated native descriptor tests. This does not certify every native chord-entry, save/load or pattern-transition path.

## Create the firmware locally

1. Obtain your own original Digitone / Digitone Keys **OS 1.44 `.syx`**. Extract it from Elektron's archive first.
2. Install Python **3.10 or newer** if necessary. No additional Python packages are required.
3. Extract one patch ZIP into its own writable folder.
4. On Windows, double-click **Create Firmware.cmd** and paste the stock `.syx` file path when asked. Alternatively run `python apply_patch.py --stock "path/to/stock.syx"` from that folder.
5. The tool checks the stock SHA-256, reconstructs the selected build, checks its SHA-256 and creates a new `.syx` beside the patch. It refuses to overwrite any existing file.

Only this stock input is accepted:

`d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659`

Expected reconstructed outputs:

- E08F: `085ef1cae6d22878da74acf4a756dd9a22389971f211208e9bd67ff349e146f8`
- E09: `2d7446c086699918ed882a7f9e52ac6e29657d09557a4be519b1500bfcd710f0`
- E09A: `68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c`

The ZIPs contain stock-dependent compressed XOR deltas, the Python patcher, a Windows launcher, metadata and instructions. They contain no complete stock or modified firmware image. The delta format is not encryption, and this packaging does not establish redistribution permission for any third-party content.

Both packages were reconstructed locally from the exact stock input and matched the existing candidate files byte for byte. Patcher error-path tests are separate from firmware execution tests. No new device trial was performed for this release. Read the included RECOVERY.md before considering any hardware trial.

Use the published SHA256SUMS.txt to check downloaded ZIPs. This verifies file integrity, not the provenance of a release downloaded from an untrusted source.
