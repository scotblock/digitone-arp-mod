# E11 — M1 synth-style step programming

Experimental original Digitone / Digitone Keys OS 1.44 build. Published 20 October 2026.
The user reported E11 working on Digitone on 19 October and patterns saving successfully on 20 October. The installed hash and individual tests were not independently verified; this is not hardware certification. Your E10 files remain
unchanged. This changes M1 programming controls, retaining E10 playback and its
per-pattern record format; M2-M4 remain unextended.

Select M1, open FUNC + SYN2, and turn D clockwise for the step page as in E10.
Programming now follows the synth arp workflow:

| Control | Action |
| --- | --- |
| Left / Right | Select the arp step |
| E | Edit that step's scale-degree offset |
| F | Arp sequence length, 1-16 |
| Up | Enable the selected step |
| Down | Make the selected step a rest |
| A / B | Explicit root / scale, retained from E10 |
| D counterclockwise | Back to main MODE / RATE / GATE controls |
| H | Step sequence ON / OFF |

C is unused on the step page; G retains the old rest-control alias. On the main
page the existing controls are unchanged. This does not add the synth arp's other
sorting modes or octave-range engine. The FUNC + SYN2 entry remains different
from the synth arp's FUNC + SYN1 entry.

The strip shows '+' enabled, '-' rest, 'X' selected enabled, '*' selected rest,
and '.' outside the chosen length. The workflow matches the synth editor; the
artwork is not a pixel-identical copy. Offsets retain E06/E10 scale-degree units.

Quick check: C Ionian, length 4, offsets 0/1/2/3, Down on step 3, sequence ON,
main MODE UP. A held single C should give C, D, rest, F. Check release/Stop,
then repeat using a sequencer trig long enough for several arp pulses.

Native PC tests cover the controls, idempotent Up/Down, cursor/length bounds,
pattern recall, exact record checksum/retained mirror and M2 isolation. The
actual E11 stock loader and native copier/init/logo run before the final
keyboard/sequencer playback test. MIDI/USB and other hardware models remain
fixtures; physical code placement/cache/timing and a new full E11 persistence/
reset suite are not established. The unchanged E10 format is not a blanket
physical compatibility guarantee.

For any separate device trial, keep a current project/sound backup, the working
E10 file and official stock 1.44 recovery available. Use a disposable project.
Use the already rehearsed startup-menu DIN route: Rubix22 MIDI OUT to Digitone
MIDI IN; hold FUNC at power-on; TRIG 4 OS UPGRADE; Elektron Transfer's SYSEX
TRANSFER / OS Upgrade via device startup menu, selecting this E11 file.
Physical MIDI is required for that route. Follow Transfer and
the device through completion; never interrupt erase/programming. First check
normal boot, menus, RECORD, ordinary sound and Stop before trying the new editor.
Recover official stock with the rehearsed procedure if startup fails; empty/
factory reset is not OS rollback. No hold-up measurement or power-system
redesign is required; inherited stock power behavior remains the agreed assumption.

[Official startup-update instructions](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer).

The accompanying stock-dependent patch ZIP reconstructs this file from the exact
official 1.44 input; it does not install it. This public package contains a stock-dependent patch, not a full firmware image. The tool never updates a device. See RECOVERY.md before any device trial.

## Create the firmware

Extract the release ZIP, run Create Firmware.cmd, and supply your own original
OS 1.44 SYX. Python 3.10 or newer is required, with no additional packages.
The tool verifies input/output hashes and refuses to overwrite existing files.

Expected output SHA-256:
`d7d3776054093b8a9b2999fc5b100c4cb88d436ab62685b6cd44770a6e4ecf75`.
