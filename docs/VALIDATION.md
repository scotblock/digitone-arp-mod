# Validation scope

This repository preserves recorded results from the working research folder. They were **not rerun simply by copying this archive**.

E09 PC coverage includes 17 native owner/driver cases, route selection off/DIN/USB/both, independent blocked-port handling, channel and route changes, shared voices, pending note-off retries, native USB packetizer/allocation failure handling, loader/startup copying and reset refusal cases. Packaged synth playback recorded 20 matching note pairs per port; packaged M1 playback recorded 11 per port.

USB endpoint submission is modeled by a fixture. Physical delivery, concurrency, cache coherence, timing and exclusive expanded-RAM ownership remain unverified. Broader reset/computed-writer coverage is incomplete.

The separate sequenced-M1 diagnostic produced no output using a host-written chord fixture. Native fixture validity and producer execution were not established. It is an unresolved investigation, not a passing test and not proof ordinary sequencing is broken.

User-reported hardware observations for E05–E08F are distinguished from PC execution results. E09 has not been reported tested on the physical device. Original/modified firmware images are omitted from this repository; SHA-256 identifiers remain in the reports.

Repository export checks validate file integrity, Python syntax and excluded file types. They do not validate firmware behavior.

## Hardware follow-up — 17 October 2026

Following the E09A download, the user reports both synth arp and MIDI-track arp output on the physical Digitone through DIN and USB. The installed hash was not independently verified. In a direct follow-up, the user confirms that M1 also arpeggiates from sequencer trigs. Physical note-off/Stop behavior remains a distinct, unconfirmed check. See outputs/Digitone-E09A-hardware-observation-2026-10-17.json.

## E10 lifecycle continuation (17 October 2026)

See [the scoped lifecycle report](../outputs/Digitone-E10-PC-lifecycle-verification.json) and [notes](../outputs/Digitone-E10-PC-lifecycle-notes.md). This covers native stopped pattern copy/paste/undo, trig clear/undo preserving settings, ten guarded reset-entry fixtures, 128 synchronized retained records and explicit stock write/cold restoration of unsaved editor changes. The stock writer is invoked through a disclosed test call frame. Automatic power-fail dispatch, physical persistence and interrupted-write recovery are not verified. No installable E10 is produced.

## E10 modeled automatic power fail (17 October 2026)

[The new evidence](../outputs/Digitone-E10-PC-powerfail-verification.json) records completed verification, not an overall safety pass: `automatic_modeled_dispatch_and_cold_restore_passed` is true while `mid_write_recovery_safe` is false. A complete interrupt-dispatched write followed by fresh cold startup restores all 128 records. A synthetic first-command cut makes the actual stock reader choose a partial image. The board pin, external interrupt, INTC2 force delivery and narrow CC/TC W1C model are disclosed fixtures; physical hold-up, final power latch and eMMC durability remain untested. See [the notes](../outputs/Digitone-E10-PC-powerfail-notes.md).

## Accepted development scope — 17 October 2026

The user accepts stock power handling as an inherited assumption and chose to keep the unit closed. A quantified hold-up measurement is not a gate to continuing E10 development. No guaranteed abrupt-loss recovery is claimed. A focused interrupt during E10 synchronization and a stopped-entry stock-helper control both leave unrecognized working-bank headers; see [the diagnostic](../outputs/Digitone-E10-PC-update-interruption-notes.md). This is recorded under the inherited interruption limitation; it is not a new power-system redesign requirement. E10 packaged loader/startup/playback integration remains outstanding.

## E10 packaged loader/startup/playback — 18 October 2026

[The consolidated report](../outputs/Digitone-E10-PC-package-integration.json) gates stock-byte-exact container reconstruction, independent MAIN decompression, SysEx packet/logical checksums, actual bootstrap entry with exact MAIN/no flash writes, native copier/init/logo/UI with strict custom ColdFire execution, 128 restored records, and native A03 keyboard/sequencer playback with 24 matching DIN/USB note pairs and balanced release/Stop. A01/A02 remain unchanged. The loader handoff and UI snapshot are serialization seams, not one uninterrupted machine; inherited input/routing/USB, clock/memory/DSP/flash and idle-scheduling fixtures remain. Physical timing/cache and device update reception are not certified. The new SYX is internal PC-only, not a hardware-ready release.
