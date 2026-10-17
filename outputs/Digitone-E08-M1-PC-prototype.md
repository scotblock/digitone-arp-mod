# E08 M1 ascending arp — PC behavior prototype

This is a host-assisted PC prototype, not an installable firmware build. E07 is unchanged.

The firmware's native MIDI input and grid-recording path creates a C–E–G trig on M1. The source hold is extended to eight native default gates through a disclosed test fixture. In OFF mode, the stock firmware sends the three-note chord unchanged. In UP mode, a Python scheduler snapshots and sorts the chord and supplies one-note descriptors to the stock MIDI task. The firmware handles MIDI output, transposition/channel selection, timed note-offs and stop cleanup. The host does not inject outgoing packets.

## Results

- OFF: 3 note-ons, 3 matching note-offs; notes [60, 64, 67]; no hanging notes.
- UP_release: 8 note-ons, 8 matching note-offs; notes [60, 64, 67, 60, 64, 67, 60, 64]; no hanging notes.
- UP_stop: 4 note-ons, 4 matching note-offs; notes [60, 64, 67, 60]; no hanging notes.

UP_release stops generating when the finite source gate expires, before the later STOP request. UP_stop interrupts an active cycle through the native transport/stop path. The step order is C E G repeated. These tests use one continuous guest session and the same native recorded chord.

## Live key-release control

Three native MIDI note-ons created the held C E G set. Three native note-offs removed it. This control ran while transport was stopped, so held-note admission did not depend on playback being active. Live source gate zero means held, and the prototype uses an explicit positive step-rate fixture rather than dividing that zero gate.

The first prototypes exposed and corrected two model errors: using half the MIDI timestamp clock and treating a held source gate as an arp rate. These were prototype errors, not changes to E07.

## What remains

The scheduler and state management must be ported to actual ColdFire helpers before this is a firmware implementation. The temporary PC descriptor arena and retirement bypass are harness mechanisms, not a verified allocation strategy. A separate native-input live test also passed: C E G were played as an ascending arp, all three source keys were released, and the active G ended 5.33 ms after the release request. No further notes appeared during the following 480 ms. Sustain, partial release, pattern replacement, mute/reset routes, other MIDI tracks, editable settings and persistent storage remain untested. E07's existing 340 bytes of fragmented padding are not assumed sufficient.

Next: execute the scheduler as machine code in isolated PC tests and connect it to the MIDI task with explicit descriptor ownership, then test live release and pattern cancellation. No E08 flashable file is produced.

## Artifacts

- [Digitone-E08-M1-OFF-PC.mid](./outputs/Digitone-E08-M1-OFF-PC.mid)
- [Digitone-E08-M1-UP_release-PC.mid](./outputs/Digitone-E08-M1-UP_release-PC.mid)
- [Digitone-E08-M1-UP_stop-PC.mid](./outputs/Digitone-E08-M1-UP_stop-PC.mid)
- [Detailed results](./outputs/Digitone-E08-M1-PC-prototype.json)

- [Live release MIDI](./outputs/Digitone-E08-M1-UP_live_release-PC.mid)
- [Combined four-case results](./outputs/Digitone-E08-M1-prototype-results.json)
