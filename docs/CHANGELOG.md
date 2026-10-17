# Build progression

- Initial OS 1.42 analysis: container framing, payloads, arp context/pitch insertion, storage lifetime, pattern ownership and PC modeling.
- Port to OS 1.44: selector/release contracts, startup/bootstrap, copier and failure handling.
- E04: physical startup stalled at logo; stock recovery succeeded. Later work identified unsupported startup instructions and revised storage/input guards.
- E05: corrected startup and scale-constrained synth arp; reported working on hardware.
- E06: scale-degree arp offsets; reported working on hardware.
- E07: synth arp DIN output; reported recorded successfully in Ableton.
- E08 family: M1 MIDI arp, own settings/controls, tempo/gate, context ownership and pattern/reset checks. E08E menu regression; E08F corrects routing. User reports working on hardware.
- E09: PC-only dual-port synth arp routing, independent port ownership and matching synth/M1 note-pair checks. M2–M4 and MIDI arp step editing remain future work.
- E09A: fixes the confirmed M1 sequence settings-source bug. Parameter-lock list pointers were being treated as full MIDI parameter records. The correction uses the consumed KitActive M1 record without adding code space or RAM. Native panel sequence controls and separate chord contracts cover the correction; physical testing remains outstanding.
- E10 prototype: native M1 1–16-step scale-degree engine, rests, clipping, wrap and native root/scale/length/step/offset/rest/enable editor. Isolated helper checks and native panel-created continuous playback pass. Temporary PC-only code/state; startup, durable pattern storage and project saving remain unfinished. No E10 firmware container is produced.

Historical notes are retained as dated research, including failed approaches. This initial import is one snapshot; it does not reconstruct a commit-by-commit history of earlier builds.
