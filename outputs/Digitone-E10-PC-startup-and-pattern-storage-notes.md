# E10 startup/reset integration and pattern-storage progress

17 October 2026. E09A remains byte-identical. No E10 SysEx container or hardware build was created.

## Implemented and tested

- Combined the step engine, atomic publisher, native editor and new lifecycle helpers into a separate decompressed PC MAIN/payload layout. The inherited native copier now copies 61,440 bytes, 26,720 more than E09A. All additions remain below the proposed reservation end at `0x47c00000`; this bound is not an ownership proof.
- The existing cold-success M1 initialization now continues to E10 initialization before the stock cache-handoff entry. E10 runtime state starts invalid in the copied image and becomes valid only after native initialization. Its sequence starts disabled, length 16, zero offsets, all steps enabled, C Ionian, and no owner.
- Native cold initialization clears the 64-byte runtime state and a 4,096-byte M1 bank with 128 records. LIVE admission, invalid admission, active/retained/held notes and an outstanding arena refuse this reset before mutation. This refuses unsafe resets; it does not implement live reinitialization or producer shutdown.
- A refused startup initializer continues to the stock handoff with the new step engine invalid and the step page closed. It does not clear the outstanding M1 arena or erase the bank. The inherited E09A M1 engine remains separate.
- Actual copier tests cover poisoned state, a wrong caller and initializer refusal. Strict ColdFire decode and MOVE checks pass. Direct-MAIN startup reaches the completed logo transition and UI. The unchanged E09A container supplies stock DSP/resources; there is no E10 loader/container proof.
- Playback from that copied startup state uses the actual native encoder editor to enter offsets `0,1,2,3`, length 4 and a rest on step 3. Keyboard and sequencer playback produce **23 matched note pairs on each port**, the expected C/D/F pitches, rests and Stop cleanup. No E10 helper, hook, settings or initialization is host-written in this playback test. Input/routing and USB endpoint fixtures remain; physical delivery is not tested.

## Pattern records: explicit APIs, not automatic recall

The native `save(slot, owner)` and `load(slot, owner)` helpers cover M1 slots 0â€“127. Both are quiescent-only. All 128 records round-trip with varied lengths, masks, roots/scales and signed offsets. Slot bounds, stale save ownership, invalid fields, damaged records and outstanding playback ownership are tested. Stock MIDI parameter records are unchanged.

Each 32-byte record contains `MS10`, schema 1, enable, length, root, scale, a reserved zero byte, the 16-bit enabled-step mask, 16 signed offsets and an unsigned byte sum. Pointers, playback/edit cursors, page state and counters are not serialized. Loading binds a new supplied owner and clears transient runtime state. The byte sum is a simple consistency check, not cryptographic integrity.

**The caller still supplies the slot and owner. There is no automatic editor-save or consumed-pattern binding adapter.** A missing/invalid record returns refusal without mutating runtime state. A future adapter must explicitly establish disabled defaults for a blank pattern and handle every refusal; it must not leave the previous sequence admitted for a different pattern.

A separate bounded PC sidecar codec tests file persistence, project-hash mismatch, schema/checksum errors and explicit PC import after a cold reset. This is a research codec, **not native Digitone project saving** and not a replacement for the requested on-device workflow. Its project identity and import are PC fixtures.

## Native persistence investigation

The stock MIDI preset encoder at `0x400081f6` clears six serialized tail bytes at `+0xa6`. E09A already uses two of them. The remaining four bytes cannot hold the step configuration; runtime `+0xa0` is stock flag data and cannot be borrowed.

Located and executed the complete stock kit encoder at `0x400095f4` and decoder at `0x400093d0`, using native restored-project parameters. Observed writes reach `+0x90e`; decoder reads reach `+0x902`. Bytes `+0x902..+0x90d` can vary with surrounding source contents in the cloned-kit control, so they remain inside the occupied writer extent.

Also executed the actual project conversion loops at `0x4000ecd6..0x4000ecf6` and `0x4000e960..0x4000e98a` through all 128 kits. These confirm serialized stride `0xa00` and runtime stride `0x988`. Source kits were cloned fixtures; this is not a project filesystem round-trip. Serialized `+0x940..+0x95f` is a **candidate** 32-byte location untouched in those controls. Nothing has been embedded there, and ownership/survival through enclosing writers is not established.

## Remaining work

1. Trace the enclosing native project writer/reader and kit-slot initialization/copy/clear paths for the candidate space. Connect a versioned extension only after those contracts are understood.
2. Bind accepted editor changes and completed pattern transitions to the correct project/pattern record. Handle blank/invalid records, pending transitions, copy/paste/undo and same-address project replacement explicitly.
3. Execute native save â†’ edit â†’ reload â†’ cold restart without PC sidecar import. Then validate a packaged loader path and the enlarged RAM region before making a firmware candidate.

Startup integration has advanced; **native per-pattern project saving remains unfinished**. Physical RAM ownership, cache coherence and timing for the enlarged E10 layout remain unverified.

## Evidence

- `Digitone-E10-PC-step-lifetime.json`
- `Digitone-E10-PC-step-bank-file.json`
- `Digitone-E10-PC-step-startup.json`
- `Digitone-E10-PC-integrated-startup.json`
- `Digitone-E10-PC-integrated-playback.json`
- `Digitone-E10-PC-persistence-route.json`
- `Digitone-E10-PC-native-kit-codec.json`

E09A SHA-256: `68f67aac272cfaa0b52763db150efddbf4654a6773e9604b627898c857fa1c3c`.
