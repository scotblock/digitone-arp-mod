# E10 packaged loader → startup → playback integration

18 October 2026. Separate internal PC loader-test package. Existing E09A and the E10 lifecycle MAIN/payload remain byte-identical. No device update or hardware release is performed.

## Package and loader

The existing E10 lifecycle MAIN and its 90,320-byte payload are copied to separate package-test paths. The native C compressor produces a 993,461-byte packed MAIN. The stock-dependent container writer reconstructs an unchanged stock 1.44 file byte-for-byte before replacing only MAIN. Other sections, including bootstrap and DSP/resources, are byte-identical to stock.

The logical ELE3 container is 1,273,856 bytes with 512-byte alignment; the SysEx file is 1,614,496 bytes. The final transport packet includes zero fill outside the advertised logical container, which is validated separately. Python decompression reconstructs MAIN exactly. Consolidated checks verify packet checksums and the advertised logical-container checksum.

The stock bootstrap executes against this actual internal package and reaches MAIN entry 0x400004e8. The reconstructed MAIN matches the lifecycle candidate exactly, and no flash writes occur in this loader run. Its own CPU registers, control registers, SRAM, written DDR and peripheral-register writes are saved in the loader handoff. That file contains firmware and is excluded from the repository.

## Native startup

The startup runner consumes this E10 handoff rather than creating the entry flags manually. It checks exact MAIN bytes before continuing, then runs the native copier, initializer, startup and logo/interface path. All copied components are checked and executed custom startup instructions receive strict ColdFire checks. There are no decompression clamps or host completion-semaphore satisfactions in the successful startup.

A private card from the preceding native automatic-writer test supplies two native-created arp programs. All 128 E10 records match after cold initialization and still match at the normal interface. The enable-sense board input is modeled as in the prior test; this does not measure the physical board or its retained power.

## Playback workload

Playback starts from that loader-derived interface snapshot. A03 is selected through the native panel so A01/A02 remain available for preservation checks. The runner programs a four-step C Ionian sequence with offsets 0, +1, +2, +3 and step 3 resting. It records a native M1 sequencer trig and also exercises keyboard input, releases and Stop. The successful run produces 24 matched note-on/off pairs per port, pitches C/D/F for the keyboard test, four sequenced arp pulses, balanced release/Stop, a valid A03 record and unchanged restored A01/A02 programs. The extra native pattern-selection work changes the scheduling phase relative to earlier 23-pair runs; fixed pair count is not the pass criterion. Correct pitches, repeated native sequenced pulses, equal ports and balanced cleanup are checked.

The first runner attempt failed because the restored project already selected a MIDI track and a blind MIDI-button toggle selected a synth track instead. The runner now reads actual selection, enters MIDI mode only if needed, and asserts M1 selection. This was a test-input correction; no firmware patch was needed. The test's minimum pulse and matched note-on/off checks remain; exact message timing is not a physical timing proof.

## What “connected” means

This is actual package bootstrap → captured loader state → native cold startup → interface snapshot → native playback. The stages use serialized state seams and rebuilt engine objects; it is not one uninterrupted physical machine. The application receives no host-loaded E10 helpers, patches, state initialization or sequence settings.

Inherited model limits remain explicit: loader flash/PLL/DDR behavior, scoped ISA adapters, the stock flash-read shortcut, DSP/peripheral models, board inputs, synthetic idle scheduling, MIDI input/routing and USB endpoint handoff fixtures. Physical cache coherence, RAM/DMA ownership, timing and device update reception are not certified by this test. Named save/reload, copy/reset and failure cases retain their earlier separate evidence; they were not all repeated here.

Stock power handling remains the accepted inherited assumption from `Digitone-E10-development-assumptions.md`; no new hold-up measurement requirement is introduced. Abrupt-loss recovery is not guaranteed.

## Artifacts and release boundary

`Digitone-E10-PC-package-integration.json` gates the package, loader, startup and playback reports. Build/test source and sanitized reports are archived; full firmware, card images, handoffs and snapshots stay outside the public repository. The internal test SYX is deliberately not supplied as a hardware-ready download. This establishes packaged PC continuity for M1, not M2–M4 support or hardware readiness.
