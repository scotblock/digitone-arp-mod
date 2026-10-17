from pathlib import Path
import json,hashlib,collections
session=json.loads(Path('outputs/Digitone-E04-PC-live-capture-session.json').read_text());contracts=json.loads(Path('outputs/Digitone-E04-PC-live-capture-contracts.json').read_text());cfg=json.loads(Path('work/os144/PC_ONLY-live-capture-layout.json').read_text());c=session['cases'][0]
checks={
 'isolated_machine_code_contracts_pass':contracts['passed'],
 'continuous_guest_session_passes':session['passed'],
 'pattern_handoff_completed':any(x['completed'] for x in c['actual_pattern_changes']),
 'receiving_index_matches_stock_pointer_index':all(x['returned_index']==x['pointer_index'] for x in c['owner_reads']),
 'captured_pattern_is_stock_derived_receiving_pattern':all(x['index_owner_matches'] for x in c['live_captures']),
 'all_live_capture_words_match_root_scale_track':all(x['matches'] for x in c['live_captures']),
 'both_receiving_patterns_captured':set(x['pattern'] for x in c['live_captures'])=={'0x407fd414','0x40813531'},
 'two_different_contexts_captured':set(x['actual'] for x in c['live_captures'])=={'0x800000be','0x80000341'},
 'all_noteon_pending_records_consumed':all(x['pending_consumed'] for x in c['descriptor_bindings'] if x['state']==1),
 'all_live_event_copies_keep_bytes_and_context':all(x['bytes_match'] and x['matches'] for x in c['live_copies']),
 'noteoff_retains_old_E_G_context_after_handoff':all(x['actual']=='0x800000be' for x in c['live_copies'] if x['state']==2 and x['original_note'] in [64,67]),
 'fresh_F_noteoff_keeps_new_context':any(x['state']==2 and x['original_note']==65 and x['actual']=='0x80000341' for x in c['live_copies']),
 'every_pitch_result_matches_oracle':all(x['matches'] for x in c['quantize']),
 'no_zero_context_at_quantizer':all(x['word']!='0x0' for x in c['quantize']),
 'live_identity_two_commits_old_context':any(x['identity']==2 and x['word']=='0x800000be' for x in c['context_commits']),
 'fresh_identity_three_commits_new_context':any(x['identity']==3 and x['word']=='0x80000341' for x in c['context_commits']),
 'old_live_pitch_retains_context_after_actual_pattern_publication':any(x['pattern']=='0x40813531' and x['word']=='0x800000be' and x['note'] in [64,67] for x in c['quantizer_owners']),
 'fresh_pitch_uses_new_pattern_context':any(x['pattern']=='0x40813531' and x['word']=='0x80000341' for x in c['quantizer_owners']),
 'guest_audio_runs_without_error':c['DSP_after']['booted'] and c['DSP_after']['error'] is None and c['audio_nonzero_bytes']>0 and c['halted'] is None,
 'existing_corrected_payload_preserved':c['payload_intact'],
 'MIDI_delivery_complete':c['MIDI_delivery']['received']==c['MIDI_delivery']['delivered'],
}
expected={'outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx':'76961a95bfa7ca97381c0ae225059f478c6fa201bd435df0785061e12dea987c','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx':'d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659','work/os144/emulator-E04-main.bin':'686dc4675e5af33f2e3b313e9101f92b914c0a848d0a858424b2d335d85b186c','work/os144/fallback-final-payload.bin':'eb908e6ae5ac26490bf4fea0216ba8fcfbff258a8f8ea0f7159342a00e14d2e7'}
hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in expected};checks['original_firmware_and_payload_hashes_unchanged']=hashes==expected
out={'PC_only':True,'flashable_firmware_produced':False,'checks':checks,'passed':all(checks.values()),'capture_count':len(c['live_captures']),'pitch_count':len(c['quantize']),'copy_count':len(c['live_copies']),'code_bytes':cfg['bytes'],'additional_state_bytes':cfg['state_bytes'],'hashes':hashes,'pattern_publications':c['pattern_publications'],'pitch_context_counts':dict(collections.Counter(x['word'] for x in c['quantize']))}
Path('outputs/Digitone-E04-PC-live-capture-summary.json').write_text(json.dumps(out,indent=2))
assert out['passed'],[k for k,v in checks.items() if not v]
report=f'''# Receiving-pattern capture and PC-only live-note fix

The live input handler supplies the receiving track's root/scale from the pattern identified by the active pattern's index at input processing. The new PC overlay captures that chosen source before input-record construction, binds the snapshot after descriptor population, and transfers it with each live queue copy. A completed pattern handoff now preserves the original context for old live notes and supplies the new context for a fresh note in this tested session.

## Stock ownership chain

`400eae88` calls `4009446a`, which reads the active pointer at `4138f214` and its pattern index at `+16119`. The input handler derives its receiving pattern at `407fd414 + index*1611d`, with track offset `track*3d0`. The stock scale eligibility read at `400eaed2..400eaee4` uses that source's root `+3cb` and raw scale `+3ce` when its branch is taken. Capture uses the already chosen A2 receiving-pattern base and D2 track at `400eaf48`, rather than reading a later global pointer at pitch output. The known note-on caller is `400eb09a`; the separate note-off caller `400eac84` does not choose a fresh pattern scale.

The executed index-return probes agree with the stock pointer's index. Captures agree with the handler's derived receiving base for both pattern 1 (`407fd414`, index 0) and pattern 2 (`40813531`, index 1). These are PC receiving-pattern fixtures, not a physical saved-project readback.

## Separate PC overlay

Added code: {cfg['bytes']} bytes at `47be3000`. Additional zero-initialized state: {cfg['state_bytes']} bytes at `47be2000` (512 bounded descriptor words plus four pending input records). This is a disposable host-installed RAM overlay after the existing startup checkpoint; it is not connected to the firmware's startup copier or reset yet.

1. `400eaf48`: capture the selected pattern/track through the existing validated capture helper. Keep a pending word keyed by the stack input-record address. Preserve registers/status and execute the two displaced stock record stores.
2. `400ff47c`: after the stock descriptor fields have been populated, bind a matching note-on pending word to its exact track/note descriptor slot and consume the pending record. Missing or mismatched note-on context clears the descriptor's word. Note-off preserves its existing word. Preserve the displaced descriptor stores and all register/condition contracts.
3. `400ff5f6` and the A5 function target loaded at `400ff5a6`: retain the stock 72-byte copy and transfer the descriptor's word into the allocated pool event. The A5 replacement also covers the two alternate copy call sites statically; those branches were not reached by this playback session.

The existing selection/cookie/pitch guards remain intact. No note event, queue eligibility or private context value was injected by the playback scenario; the new helpers execute their actual machine code. Host changes are the overlay installation, root/scale pattern fixtures and MIDI input configuration.

## Results

{len(checks)} summary checks pass, plus {len(contracts['checks'])} isolated contract groups: all 512 descriptor slots, invalid addresses/gaps, track/note/root/scale/readiness validation, pending-key mismatch, note-off preservation, and stock-equivalent memcpy bytes, registers, stack and full status across failure controls. New instruction encodings pass the ColdFire decoder and combined MOVE operand restrictions.

The continuous restored-project guest session produces three accepted note-on captures: E64 and G67 take root 62/raw scale 0 (`800000be`) from pattern 1; fresh F65 takes root 65/raw scale 5 (`80000341`) from pattern 2. All three pending records are consumed at descriptor binding. Seven actual direct descriptor copies preserve bytes and expected metadata, including note-off after replacement. The active pattern pointer genuinely changes; old E/G arp pitches continue using their original context while the pointer identifies pattern 2. The fresh F commits and pitches with pattern 2's context.

All {len(c['quantize'])} quantizer results match the independent scale oracle, with zero missing-context calls (48 old-context calls and 5 new-context calls). The played live E/G/F pitches already belong to their corresponding scales, so this run proves correct context delivery/retention rather than an out-of-scale live offset being corrected. The sequencer C60 changes to 59. Actual DSP execution remains booted with {c['DSP_after']['renders']} renders, nonzero audio, no DSP error and no emulated halt.

## Limits and next bounded step

The direct live creator branch is observed; alternate cached replay copies are covered by the wrapper's isolated contract and static hook target, not by full alternate-selector execution. Allocation failure/exhaustion is not newly exercised; binding precedes allocation and does not rely on its success. Arbitrary producer interleavings across the stock byte-copy interval are not certified by this input sequence. Other computed callers, additional tracks in full playback, and a live nonzero arp-step offset need broader execution coverage.

New sidecar lifetime is initialized by the PC installer only. Next connect its initialization/reset and code copying to the corrected PC startup path, and test failure/reset plus copy-source serialization before considering packaging. Physical RAM ownership, cache coherence, timing and the original device startup failure remain unresolved. E04 and stock firmware hashes are unchanged, no new `.syx` is produced, and no hardware retry is implied.

Evidence: `Digitone-E04-PC-live-capture-session.json`, `Digitone-E04-PC-live-capture-contracts.json`, `Digitone-E04-PC-live-capture-summary.json`; builder and test scripts under `work`; raw overlay and layout under `work/os144/PC_ONLY-live-capture-*`.
'''
Path('outputs/Digitone-E04-PC-live-capture-review.md').write_text(report)
print('PASS',len(checks),'summary checks;',len(c['quantize']),'valid-context pitch calls')
