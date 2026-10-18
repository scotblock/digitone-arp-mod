# E10 — controlled Digitone hardware trial

18 October 2026. Original Digitone / Digitone Keys, OS 1.44 only.

This is an experimental trial candidate, not a hardware-certified release. Its
bytes are identical to the E10 package that passed the PC loader, startup,
playback and edit/save/restart/recall tests. Renaming the file adds no code.
No device was contacted while preparing this folder. The startup screen may
still say 1.44; identify this build by its file/hash, not that display.

## What changes

E10 retains E09A's synth arp scale-degree behavior and synth/M1 output routing.
It adds M1's 1–16-step scale-degree offsets, rests, explicit root/scale controls
and per-pattern project storage. M2–M4 arps and direct trig-key step selection
are not implemented. Main arp MODE/RATE/GATE remain separate from the step page.
Step mode OFF retains the ordinary ascending arp.

## Before this trial

Keep a current external backup of important projects/sounds and use a disposable
project for E10 saves. You previously completed the stock update rehearsal and
successfully recovered stock after E04; no repeat rehearsal is requested here.
Have the official stock 1.44 file available before sending E10. Verify its hash
against Digitone-E10-hardware-trial-recovery.md. An OS file is not a project backup. Returning to stock is not
a promise that custom E10 settings survive stock editing/re-saving a project.

Residual risks are startup failure, stuck/wrong MIDI notes, audio faults,
corrupted project data and a failure requiring service. Physical RAM ownership,
cache execution and worst-case timing are not established by the PC tests.
Stock power handling remains the accepted inherited assumption; no new power
protocol or abrupt-loss guarantee is claimed. E04's prior successful stock
recovery does not guarantee recovery from every failure.

## Install using the rehearsed startup MIDI route

1. Close Ableton, loggers and other MIDI apps. Connect Rubix22 USB to the PC and
   **Rubix22 MIDI OUT → Digitone MIDI IN**. Disconnect Digitone USB during this
   transfer; leave audio monitoring low.
2. Hold **FUNC** while powering on; select **TRIG 4: OS UPGRADE**.
3. In Elektron Transfer open **SYSEX TRANSFER → OS Upgrade via device startup
   menu**, choose the Rubix22 MIDI interface as instructed, and select
   `Digitone_OS1.44E10_M1_STEPS_HARDWARE_TRIAL.syx` from this folder.
4. Follow Transfer/device prompts through completion. Do not interrupt erase or
   programming. The file's 1,614,496 bytes alone require about 8.6 minutes at
   standard MIDI wire speed; sender pauses/programming add time. A long transfer
   alone is not a hang. Do not use a fixed timeout to power-cycle an update.

The startup route requires physical MIDI, not device USB. Sources:
[Elektron Transfer guidance](https://support.elektron.se/support/solutions/articles/43000662701-how-to-update-your-device-via-sysex-transfer),
[Digitone manual, printed page 81](https://www.elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).

## First checkpoint — boot and ordinary operation

After update completion, first confirm that the logo clears and the normal
interface appears. Check normal synth sound, RECORD/sequence entry, TRIG/SYN1/
SYN2/FLTR/AMP/LFO pages on synth and MIDI tracks, and Stop. Report this result
before expanding the test. A persistent logo, broken menus or failed RECORD is
a failed checkpoint; use Digitone-E10-hardware-trial-recovery.md rather than trying resets or another mod.

## Second checkpoint — M1 step playback

Reconnect the preferred MIDI monitoring connection after installation. Avoid
routing MIDI back to the Digitone. Select M1 and set an external receiver/Ableton
to its output channel. Check DIN and USB separately to avoid recording duplicate
messages when both paths feed the same track.

From an ordinary M1 parameter page, press **FUNC + SYN2**. Set the main arp to
UP, a moderate rate such as 1/16 and gate 50. Turn **D clockwise** to the step
page. These are the step-page encoders:

| Encoder | Setting |
| --- | --- |
| A | Root |
| B | Scale |
| C | Length, 1–16 |
| D counterclockwise | Return to main arp page |
| E | Select step |
| F | Selected step's offset, -24 to +24 scale degrees |
| G | Selected step's rest on/off |
| H | Step sequence on/off |

Choose C / Ionian, length 4, offsets **0, 1, 2, 3**, rest on step 3 only, and
step sequence ON. Holding a single C should produce **C, D, silence, F** per
cycle. Octave labels differ between applications. Release the note and press
Stop: the last note must end. Repeat using a sequencer trig long enough to
contain several arp pulses. Keep the synth arp working as before.

## Third checkpoint — pattern ownership and saving

In a second disposable pattern use C / Ionian, length 4, offsets **0, 2, 4, 6**,
no rests: a single C should produce **C, E, G, B**. Alternate the two patterns,
including during playback, and wait for the pattern change to complete. Check
that offsets/rests belong to the receiving pattern and notes end on release/Stop.

Save the project to an unused slot, reload it and check both programs. Then do
an ordinary completed shutdown/restart and reload the saved project. For a
complete restart the manual specifies at least 30 seconds off before power-on;
this is not an instruction to interrupt an update. Recheck both programs.
On disposable patterns, copy/paste and undo should carry/restore the program;
pattern trig clear/undo retains arp settings, following the stock behavior.
Do not deliberately cut power during saving or use factory/empty reset as tests.

Record pass/fail and exact steps in Digitone-E10-hardware-trial-results-template.md. Stop on a new freeze,
menu error, stuck note, wrong recall or repeatable audio fault. No further
stress test is needed until these three checkpoints pass.

## Patch ZIP alternative

The local SYX is ready as a trial file. The accompanying patch ZIP is for sharing
without a full firmware image. Extract it into a writable folder, double-click
Create Firmware.cmd, and supply your own exact official OS 1.44 SYX. Python
3.10+ is required. The tool verifies input/output hashes, refuses overwrites and
never sends MIDI or USB. Automatic GitHub source ZIPs are not this patch package.

No GitHub release or hardware update was performed by this preparation.
