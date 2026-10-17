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

- E10 startup/storage continuation: integrated native cold copying/initialization and safe reset refusal; direct-MAIN logo/UI and panel-programmed playback pass with 23 matched pairs per port. Native explicit M1 128-pattern record APIs and a separate PC sidecar codec pass. Stock kit/project conversion loops identify a possible serialized extension location; automatic pattern binding and native save/load remain unfinished. E09A is unchanged; no E10 container.

- E10 storage verification: 128 diagnostic records at serialized kit +0x940 survive native named save/load and a fresh cold boot followed by named reload, on private emulator cards. Stock runtime decoding remains byte-identical, but stock decode/re-encode and cold working-cache restoration lose the records. Both persistence bridges remain unimplemented; E09A is unchanged.

- E10 native persistence bridge: machine-code project capture/emission preserves 128 records through native named load/save and retained RAM mirror rebuild. An explicitly invoked stock cache writer followed by fresh cold PC startup restores all 128; automatic power-loss dispatch is not established. Copied-image playback still produces 23 matching DIN/USB note pairs. Editor-to-bank publication and pattern recall remain unconnected. No installable E10 firmware; E09A unchanged.

- E10 editor/bank/recall continuation: native accepted step edits commit checksummed records to exact project-kit slots with generation binding. Native panel-created A01/A02 programs save and reload independently, including discarding an unsaved change; the load confirmation was continued from the test checkpoint. A confirmed running handoff keeps a three-note held chord and selects the receiving saved program; release/Stop cleans up. Playback remains 23 matching note pairs per port. Copy/clear/reset, incremental persistence and hardware readiness remain separate. E09A unchanged; no E10 container.
