# E09 â€” DIN + USB arp routing (PC candidate)

17 October 2026. E08F remains the preserved user-reported working baseline. E09 is a separate PC/Digiemu candidate; no tool transmitted firmware or updated the Digitone.

## Routing change

Both arp types follow the normal output selection: DIN MIDI, USB MIDI, or both. Enable both outputs when testing both connections. A USB cable is not required for DIN operation. The M1 arp already uses the stock MIDI-track fanout; the synth arp mirror previously bypassed it and wrote only to DIN.

The synth mirror now has independent DIN and USB voice ownership. If the output channel/selection changes during a held note, each accepted output keeps its original release destination. A full/unavailable port does not prevent the other from operating. Pending note-offs retry only on their own port. Shared synth voices still emit one note pair per port. The working E08F menu corrections are byte-for-byte preserved.

The candidate adds 2,464 copied bytes, including 160 bytes of USB owner state, inside the proposed reservation. This is not proof of physical ownership of the expanded region.

## PC evidence

The actual stock fanout and drivers passed the off/DIN/USB/both matrix. Seventeen native ownership/driver cases cover channel/route changes, shared voices, blocked ports, USB disconnect, pool exhaustion/busy descriptors, endpoint rejection, pending note-off retries and USB buffer wrap. The native USB packetizer, descriptor allocator and failure cleanup execute; endpoint acceptance is a fixture.

The packaged loader reaches MAIN, native copying/initialization reaches the UI, and nine stopped diagnostic/reset cases preserve the complete watched payload, including a pending USB-owner fixture. On the packaged startup state, continuous synth playback produces **20 matching note pairs on each port**, and M1 produces **11 matching pairs**. No routing helper is host-loaded in these final packaged checks. These are data/pairing results, not physical USB delivery or timing measurements.

## M2â€“M4 investigation

The actual stock MIDI handle getter was executed for all four tracks. Each has a separate parameter record and output channel. The extension currently hardcodes M1's handle, cache slot, settings owner and one scheduler/arena. Broadening the menu predicate alone would share held notes, timing and settings incorrectly.

The next implementation needs four independent held/sustain sets, rate/gate/step cursors, source/request owners and retiring event arenas. At the current sizes, three extra states/arenas would add at least 1,224 bytes before step data. The UI must bind to the page's intended MIDI track and preserve all ordinary menus. Stop must retire all four tracks; releasing one must leave the others playing. These features are **not added in E09**.

## Synth-style MIDI arp sequencer

Two separate behaviors need coverage: ordinary pattern chord trigs feeding the arp, and an arp editor with programmable pitch offsets, rests and sequence length. A 16-step editor needs at least 19 new saved bytes per MIDI track (16 signed offsets, a 16-bit enable/rest mask and one length byte), before metadata/versioning. The existing two-byte MODE/RATE/GATE tag cannot hold that sequence.

New owned serialized storage, native save/load/import handling and per-track editor accessors are required. Reusing synth arp callbacks would repeat the earlier synth-T4 alias problem; taking CC fields would displace existing MIDI features. Pitch-offset semantics and MIDI root/scale access also need explicit validation before claiming E06-style scale degrees. No MIDI step editor or new saved-project schema is implemented in E09.

## Sequenced-chord diagnostic

A separate E09 diagnostic using a host-written runtime chord fixture produced no MIDI on either port. That fixture was not entered by the native panel, and its validity/producer execution were not established, so this is not proof that ordinary MIDI sequencing is broken. It leaves the chord-to-arp path unverified. The next test should create/record the chord through the native sequencer and trace its producer/consumer context before expanding to M2–M4.

## Next checks

Use Digiemu first to check both output paths and the unchanged menus. Physical dual-port recording remains outstanding. Continue with sequenced MIDI chord production/context capture before implementing M2â€“M4, then add the step editor and saving as a separate change. The generated test project remains a draft; this routing change does not certify its import or settings persistence.

File: `Digitone_OS1.44E09_DUAL_PORT_ARP_PC_ONLY.syx`. SHA-256: `2d7446c086699918ed882a7f9e52ac6e29657d09557a4be519b1500bfcd710f0`.
