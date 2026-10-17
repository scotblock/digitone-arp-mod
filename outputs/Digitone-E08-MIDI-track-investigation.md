# Independent MIDI-track arp investigation

E07 remains unchanged. The user reports that E07 runs on the physical Digitone and its synth arp MIDI output records in Ableton. This is a user observation, not a complete hardware timing or ownership certification.

## What was observed

A continuous PC run used E07 with a MIDI track selected through the native UI, enabled M1 channel 1 and recorded a C trig. It emitted two C note-ons and two matching velocity-zero note-offs. The observed gates were approximately 123 and 125 ms. Neither the actual 1.44 synth arp selector nor its offset hook executed in that workload. Earlier exploratory probes included historical or tentative addresses; their zero-hit counts are not used as proof.

The actual MIDI task consumes queued descriptors, applies track gates/channel selection/transposition, emits notes through its stock packet buffer, and schedules timed releases. The note-on packet append returned to 0x400f4858 and its matching timed release append returned to 0x400f4ab0. Candidate interception at 0x400f42da is before these steps; no interception has been implemented.

The existing synth selector indexes four 40-byte records and reads arp settings from a Sound structure. MIDI parameter records have a different layout. Merely opening the synth arp menu on MIDI tracks or passing indexes 4–7 is not an established implementation route.

## Proposed first prototype

Use a separate M1 arp state, initially with explicit PC settings fixtures: OFF preserves the stock chord; UP turns a three-note chord into successive notes. Feed generated notes into the stock MIDI scheduling/output path, with finite gates and cancellation when the source ends, playback stops or a new pattern replaces it. Reuse E06 scale-degree mathematics after MIDI root/scale ownership is traced. Extend to M2–M4 after the first independent engine works.

Settings must eventually be editable and survive pattern/project operations. Synth arp parameters are part of Sounds; MIDI tracks do not have a matching Sound container. The settings page, storage format and reset rules require a deliberate design. Stock project serialization will not be changed based only on apparent unused bytes.

## Space constraint and next target

The E07 allocation plan has only 340 fragmented padding bytes left, with a largest gap of 256 bytes. That is a concrete layout constraint, not a total-device free-space measurement. An independent engine cannot be assumed to fit there. Code consolidation or another audited placement will be needed once the prototype's actual size is known.

Next: trace the queued chord producer and stock MIDI timing messages, then run a one-track UP prototype with native chords, release and stop cancellation. No new firmware has been packaged.

## Evidence

- [Digitone-E08-MIDI-track-queue-trace.json](./outputs/Digitone-E08-MIDI-track-queue-trace.json)
- [Digitone-E08-MIDI-track-feasibility.json](./outputs/Digitone-E08-MIDI-track-feasibility.json)

Official stock feature reference: [Digitone manual, arp and MIDI-track sections](https://elektron.se/wp-content/uploads/2024/09/Digitone_User_Manual_ENG_OS1.41_231108.pdf).
