# Digitone 1 — E08E ARP TESTS

**DRAFT — format validated; playback acceptance failed in the PC fixture.** The bounded A02 test emitted no MIDI note-ons after UP was entered on the panel. Its active UI tag became UP while the playback context remained OFF. The cause is unresolved. Do not use this project's results to approve a firmware hardware trial, and do not assume the sequences will emit MIDI without further investigation. This file is provided as a reviewable project draft, not a verified working test suite.

This is a **project**, not an OS update. It contains 16 named test patterns in bank A for the original Digitone / Digitone Keys. Tempo is 120 BPM, with 16 steps per pattern. Banks B–H have no programmed notes.

The custom MIDI arp controls require **our E08E build**. M1 is the only MIDI track with an added arp; M2–M4 remain ordinary MIDI tracks. **The full PC project-restore test resets the saved custom M1 settings to OFF, 1/16, 50%. Enter the table's MODE, RATE and GATE on M1 after selecting each test pattern.** The notes and pattern names are preprogrammed; automatic restoration of the custom controls is not working in this tested path. Stock firmware and E07 will not interpret the custom settings. This project does not establish that E08E is hardware-ready or authorize installing firmware.

## Import and routing

1. Save your current work, then use Elektron Transfer to transfer **Digitone_E08E_ARP_TESTS.dnprj** to an unused project location on the Digitone's +Drive. Load **E08E ARP TESTS** from the project menu. Do not send this file through the OS-upgrade menu.
2. For MIDI recording, connect **Digitone MIDI OUT → Rubix22 MIDI IN**. Enable the Digitone's DIN MIDI output in its global MIDI settings. These global port/clock settings are not configured by this project.
3. In Ableton, enable Track input for Rubix22. Create a MIDI track with **MIDI From: Rubix22, channel 9**, arm it and set its output to **No Output** while recording. This prevents MIDI echo. To hear the MIDI arp, use a software instrument or an external synth.
4. The file encodes **M1 channel 9**, but the tested PC restore path returned channel 1. On each test pattern, select M1, open SYN1 and enable/set **CHAN to 9**; inspect its displayed value. The A13 bypass test requires **M2 channel 10**, which you should also enable/set on M2's SYN1 page. Treat these as manual setup requirements until project import is verified. M1 does not produce an internal Digitone synth voice. A14/A15 also contain a T1 synth sequence, heard from the Digitone's audio outputs.
5. First select A01 with playback stopped. Select M1 and open **FUNC + SYN2**: set MODE OFF, RATE 1/16, GATE 50. For A02, set UP, 1/16, 50. For each following pattern, enter the target settings in the table. Inspect the displayed values rather than relying on encoder turn counts. Keep keys released while changing MODE, then send fresh input.

## Pattern checklist

Run A01 and A02 first. Record a few bars, press Stop, and check that the final notes end. Continue to the other tests only after those basics work. **The settings below are the targets to enter, not verified automatic presets.** The more demanding patterns are provided for later coverage, not as instructions to run every setup in a first hardware trial.

| Pattern | Name | Settings / purpose |
|---|---|---|
| A01 | 01 OFF CHORD | M1 OFF. C–E–G chord once per bar; baseline simultaneous notes. |
| A02 | 02 UP MEDIUM | M1 UP, 1/16, gate 50%. Expect ascending C–E–G cycling. |
| A03 | 03 UP SLOW | Same chord, 1/8, gate 50%. |
| A04 | 04 UP FAST | Same chord, 1/32, gate 50%. |
| A05 | 05 SHORT GATE | UP, 1/16, gate 10%. Compare note lengths with A02. |
| A06 | 06 LONG GATE | UP, 1/16, gate 90%. Compare note lengths with A02. |
| A07 | 07 EIGHT NOTES | UP, 1/16. Eight-note C-major chord, MIDI notes 60, 62, 64, 65, 67, 69, 71, 72. |
| A08 | 08 WIDE CHORD | UP, 1/16. MIDI notes 48, 60, 67, 72 test octave spacing. |
| A09 | 09 RETRIGGER | UP, 1/16. Short C–E–G chords at steps 1, 5, 9, 13. |
| A10 | 10 LIVE INPUT | Empty M1 sequence; UP, 1/16, gate 50%. For held-note, release, sustain and Stop tests. |
| A11 | 11 HANDOFF SLOW | C–E–G, UP, 1/8, gate 20%. Later compare a completed handoff to A12. |
| A12 | 12 HANDOFF FAST | C–E–G, UP, 1/32, gate 80%. Later compare a completed handoff to A11. |
| A13 | 13 M2 BYPASS | M1 OFF/empty. M2 sends ordinary repeated C notes on channel 10; no M2 arp. |
| A14 | 14 SYNTH CHECK | M1 OFF/empty. T1 plays a simple four-note synth sequence for an audio baseline. |
| A15 | 15 SYNTH AND M1 | T1 synth sequence plus M1 UP, 1/16, gate 50% to check simultaneous operation. |
| A16 | 16 BLANK OFF | Empty sequence with M1 OFF. Useful quiet comparison. |

For A01–A08 and A11/A12/A15, the M1 chord starts at step 1, lasts 15 steps and leaves a one-step gap before repeating. A09 uses two-step chords. A13/A14/A15's simple repeated notes are one step long. MIDI note 60 is used as C; octave names differ between applications.

At 120 BPM, nominal arp spacing is 250 ms at 1/8, 125 ms at 1/16 and 62.5 ms at 1/32. At 1/16, gates 10%, 50% and 90% nominally correspond to 12.5, 62.5 and 112.5 ms. Recorded timing can include firmware scheduling, MIDI serialization and computer/interface jitter.

## A10 live release / sustain / Stop

Select M1. Use its live note entry, or send a held C–E–G chord to the Digitone's **configured AUTO channel**. Check the device's actual AUTO-channel setting; this project does not change it. For external input use Rubix22 MIDI OUT → Digitone MIDI IN, while recording the return on channel 9 with no MIDI echo.

Check these separately: release the chord; hold sustain, release the chord, then release sustain; press Stop while holding a chord; set MODE OFF while notes are held. Release all input keys and sustain before enabling UP again, then send a fresh chord. Check the recording for missing note-offs or new notes continuing unexpectedly. A10 contains no sequenced notes, so output requires fresh input.

For A11/A12, first enter their target settings while stopped and check that switching between them retains those edits within the session. Only then try a playing handoff. Inspect settings and output after the pattern has actually changed, rather than when its button is first pressed. Stop and release input before leaving the test project. For saved-settings testing, save a disposable copy, reload it and compare A01/A02's displayed settings; that physical save/reload round trip has not been verified here, and the PC restoration gap remains open.

## Validation and limits

The project passed DN1 structural parsing, exact decompression round trip, ZIP integrity and two independent payload/CRC checks. All 128 pattern note masks, the first 16 pattern names/settings records and intended chords were checked. The MIDI settings records were encoded and decoded with native OS 1.44 code plus the tested E08E extension bridge. Existing default sounds and the opaque project tail were preserved.

Native restoration/startup and the bounded playback check are recorded in the adjacent validation reports. The project name and named patterns reached native runtime memory, but the custom M1 settings tag did not reach the active settings record; it returned zero/OFF, and the output channel returned 1. The subsequent manual-UP playback attempt emitted no MIDI note-ons; the private playback context stayed OFF. Stop returned transport to stopped with no retained arp members, but this is not meaningful note-release proof when no notes were emitted. Passing the individual MIDI codec test did not establish full-project settings persistence or integrated playback. The test inserts the flat image into a saved-project mirror; it does not exercise Elektron Transfer or the complete device project-import path. The reason the MIDI preset fields did not reach the active kit is unresolved, so this is not proof that the normal import path will behave identically. **Physical import, physical playback of this project, and a physical save/reload remain unverified.** No firmware was changed or sent to the Digitone while creating it.

Project SHA-256: `14a48c5266d67fcddf78d7db937de538dc8d99efbd13c455abad6a1090f8a5fa`.

Project-format tooling: [DNX by NoiseAndMatter](https://github.com/NoiseAndMatter/DNX), AGPL-3.0-or-later, source commit `5512058d87b5cf5b46b3ad0c51d929fcf9051172`. Generated project content and independent validation are local to this task.
