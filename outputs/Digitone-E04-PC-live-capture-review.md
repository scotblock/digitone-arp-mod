# Receiving-pattern capture and PC-only live-note fix

The live input handler supplies the receiving track's root/scale from the pattern identified by the active pattern's index at input processing. The new PC overlay captures that chosen source before input-record construction, binds the snapshot after descriptor population, and transfers it with each live queue copy. A completed pattern handoff now preserves the original context for old live notes and supplies the new context for a fresh note in this tested session.

## Stock ownership chain

`400eae88` calls `4009446a`, which reads the active pointer at `4138f214` and its pattern index at `+16119`. The input handler derives its receiving pattern at `407fd414 + index*1611d`, with track offset `track*3d0`. The stock scale eligibility read at `400eaed2..400eaee4` uses that source's root `+3cb` and raw scale `+3ce` when its branch is taken. Capture uses the already chosen A2 receiving-pattern base and D2 track at `400eaf48`, rather than reading a later global pointer at pitch output. The known note-on caller is `400eb09a`; the separate note-off caller `400eac84` does not choose a fresh pattern scale.

The executed index-return probes agree with the stock pointer's index. Captures agree with the handler's derived receiving base for both pattern 1 (`407fd414`, index 0) and pattern 2 (`40813531`, index 1). These are PC receiving-pattern fixtures, not a physical saved-project readback.

## Separate PC overlay

Added code: 474 bytes at `47be3000`. Additional zero-initialized state: 2080 bytes at `47be2000` (512 bounded descriptor words plus four pending input records). This is a disposable host-installed RAM overlay after the existing startup checkpoint; it is not connected to the firmware's startup copier or reset yet.

1. `400eaf48`: capture the selected pattern/track through the existing validated capture helper. Keep a pending word keyed by the stack input-record address. Preserve registers/status and execute the two displaced stock record stores.
2. `400ff47c`: after the stock descriptor fields have been populated, bind a matching note-on pending word to its exact track/note descriptor slot and consume the pending record. Missing or mismatched note-on context clears the descriptor's word. Note-off preserves its existing word. Preserve the displaced descriptor stores and all register/condition contracts.
3. `400ff5f6` and the A5 function target loaded at `400ff5a6`: retain the stock 72-byte copy and transfer the descriptor's word into the allocated pool event. The A5 replacement also covers the two alternate copy call sites statically; those branches were not reached by this playback session.

The existing selection/cookie/pitch guards remain intact. No note event, queue eligibility or private context value was injected by the playback scenario; the new helpers execute their actual machine code. Host changes are the overlay installation, root/scale pattern fixtures and MIDI input configuration.

## Results

22 summary checks pass, plus 7 isolated contract groups: all 512 descriptor slots, invalid addresses/gaps, track/note/root/scale/readiness validation, pending-key mismatch, note-off preservation, and stock-equivalent memcpy bytes, registers, stack and full status across failure controls. New instruction encodings pass the ColdFire decoder and combined MOVE operand restrictions.

The continuous restored-project guest session produces three accepted note-on captures: E64 and G67 take root 62/raw scale 0 (`800000be`) from pattern 1; fresh F65 takes root 65/raw scale 5 (`80000341`) from pattern 2. All three pending records are consumed at descriptor binding. Seven actual direct descriptor copies preserve bytes and expected metadata, including note-off after replacement. The active pattern pointer genuinely changes; old E/G arp pitches continue using their original context while the pointer identifies pattern 2. The fresh F commits and pitches with pattern 2's context.

All 53 quantizer results match the independent scale oracle, with zero missing-context calls (48 old-context calls and 5 new-context calls). The played live E/G/F pitches already belong to their corresponding scales, so this run proves correct context delivery/retention rather than an out-of-scale live offset being corrected. The sequencer C60 changes to 59. Actual DSP execution remains booted with 18805 renders, nonzero audio, no DSP error and no emulated halt.

## Limits and next bounded step

The direct live creator branch is observed; alternate cached replay copies are covered by the wrapper's isolated contract and static hook target, not by full alternate-selector execution. Allocation failure/exhaustion is not newly exercised; binding precedes allocation and does not rely on its success. Arbitrary producer interleavings across the stock byte-copy interval are not certified by this input sequence. Other computed callers, additional tracks in full playback, and a live nonzero arp-step offset need broader execution coverage.

New sidecar lifetime is initialized by the PC installer only. Next connect its initialization/reset and code copying to the corrected PC startup path, and test failure/reset plus copy-source serialization before considering packaging. Physical RAM ownership, cache coherence, timing and the original device startup failure remain unresolved. E04 and stock firmware hashes are unchanged, no new `.syx` is produced, and no hardware retry is implied.

Evidence: `Digitone-E04-PC-live-capture-session.json`, `Digitone-E04-PC-live-capture-contracts.json`, `Digitone-E04-PC-live-capture-summary.json`; builder and test scripts under `work`; raw overlay and layout under `work/os144/PC_ONLY-live-capture-*`.
