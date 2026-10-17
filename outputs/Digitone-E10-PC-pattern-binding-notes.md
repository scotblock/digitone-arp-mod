# E10 editor-to-bank and pattern recall

17 October 2026. Separate decompressed PC prototype. E09A is unchanged. No installable E10 firmware was produced.

## Connection

Accepted step-editor changes now serialize a validated 32-byte record directly into the corresponding slot of the existing 128-pattern M1 bank. Full native project serialization emits these records using the preceding persistence helpers. Recall reads that bank when the editor binds a different pattern or when the actual MIDI consumer selects a different playback owner.

Pattern identity is derived from the exact M1 settings pointer within the captured runtime project's kit array: project base `+0xb08e9c`, kit stride `0x988`, M1 settings `+0x5ce`. Only exact kit-slot pointers resolve. Adjacent MIDI-track records, misaligned pointers and pointers outside the 128-slot array refuse. The captured project generation is part of the binding, so replacing a project at identical addresses forces a new recall.

New adapters begin at `0x47bf1400`; their ownership metadata is at `0x47bf3800`. The copied payload is 79,904 bytes. These are PC candidate addresses; exclusive physical RAM ownership has not been certified.

## Admission and publication

- Consumed recall follows the existing native selected-owner helper. It does not treat a queued panel request as a completed handoff. It permits the held set to continue but requires matching consumed ownership and no outstanding arena descriptor. Refusal invalidates step ownership, allowing the existing ordinary arp route to continue. A later eligible owner-selection call can retry; no periodic retry hook has been added.
- An editor binding change refuses while M1 has active or held notes, an outstanding arena, or a different running consumed owner. Existing-owner edits retain the earlier publisher's checks.
- Publication and record commit form one interrupt-masked operation. The private serializer uses the original validated record encoder without its quiescence checks; this variant is called only from the owned publisher and does not mutate held notes, the arena, transport or M1 playback ownership. The public quiescent RAM APIs remain unchanged.
- Blank or malformed records produce disabled defaults and fresh cursors. Playback pointers, edit cursors and counters are not serialized.
- The editor invokes the native M1 parameter-handle change notification after a setting edit. Drawing and that callback run outside the protected record-copy section. Cursor/page controls do not invoke the setting-change notification.
- Render admission closes the step view if a different active owner prevents editor binding. Merely viewing a blank pattern may materialize a disabled default record; this does not enable its step sequence.

## PC evidence

The source/tests and JSON reports accompany this note. The consolidated report is `Digitone-E10-PC-pattern-binding-verification.json`.

1. Native helper contracts cover all 128 exact owner mappings, rejected aliases, two distinct records, blank defaults, same-address project replacement, retained notes, pending editor refusal, outstanding-arena refusal/retry, missing project ownership and caller interrupt-status restoration. The isolated notification handle has no subscriber graph; real callbacks are exercised in the panel scenario.
2. Cold startup copies the new code and zero metadata, performs native initialization/project capture and completes the logo/UI transition. This uses direct MAIN with E09A DSP/resources, not a packaged E10 loader path.
3. The native panel creates A01 (length 15, first offset +1, C Ionian) and A02 (length 16, first offset -1, C-sharp Ionian), enables both step programs, and recalls each independently. Native Save Project As saves them. A01 is changed to +2 without saving; native project reload restores the +1 record and advances the project generation. Opening both patterns recalls their saved programs. No record, bank, settings or hook data are inserted by the runner. The scenario resumed its own native checkpoint at the load confirmation after an initial test-button error; saved storage overlays and machine state were retained.
4. Panel-programmed keyboard and sequencer playback still produces 23 matched note-on/off pairs per port, with identical DIN and USB note messages. Inherited emulator input/routing/USB endpoint fixtures remain disclosed in that report; physical port timing is not implied.
5. The running-handoff report separately checks a native pattern backing change, actual consumed-owner recall with a held chord, preservation of the two bank records, and release/Stop cleanup. It is one transition workload, not exhaustive coverage.

## Remaining scope

Full named-project saving and recall are the tested persistence route. Incremental mirror updates and unsaved power-loss recovery are not verified. Copy/clear/undo and exceptional reset/project-replacement paths still need adapters or targeted checks. Physical RAM ownership, cache behavior and timing remain separate, and no hardware-ready E10 build is claimed.
