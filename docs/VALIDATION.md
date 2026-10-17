# Validation scope

This repository preserves recorded results from the working research folder. They were **not rerun simply by copying this archive**.

E09 PC coverage includes 17 native owner/driver cases, route selection off/DIN/USB/both, independent blocked-port handling, channel and route changes, shared voices, pending note-off retries, native USB packetizer/allocation failure handling, loader/startup copying and reset refusal cases. Packaged synth playback recorded 20 matching note pairs per port; packaged M1 playback recorded 11 per port.

USB endpoint submission is modeled by a fixture. Physical delivery, concurrency, cache coherence, timing and exclusive expanded-RAM ownership remain unverified. Broader reset/computed-writer coverage is incomplete.

The separate sequenced-M1 diagnostic produced no output using a host-written chord fixture. Native fixture validity and producer execution were not established. It is an unresolved investigation, not a passing test and not proof ordinary sequencing is broken.

User-reported hardware observations for E05–E08F are distinguished from PC execution results. E09 has not been reported tested on the physical device. Original/modified firmware images are omitted from this repository; SHA-256 identifiers remain in the reports.

Repository export checks validate file integrity, Python syntax and excluded file types. They do not validate firmware behavior.

## Hardware follow-up — 17 October 2026

Following the E09A download, the user reports both synth arp and MIDI-track arp output on the physical Digitone through DIN and USB. The installed hash was not independently verified. In a direct follow-up, the user confirms that M1 also arpeggiates from sequencer trigs. Physical note-off/Stop behavior remains a distinct, unconfirmed check. See outputs/Digitone-E09A-hardware-observation-2026-10-17.json.
