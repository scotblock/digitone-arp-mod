import json,hashlib
from pathlib import Path
def read(name):return json.loads(Path('outputs/'+name+'.json').read_text())
cap=read('Digitone-OS1.44-caller-state-capture');natural=read('Digitone-OS1.44-real-selector-caller');fixture=read('Digitone-OS1.44-real-selector-context')
assert cap['failure'] is None and natural['passed'] and fixture['passed'] and natural['failure'] is None and fixture['failure'] is None
assert len(natural['cases'])==8 and len(fixture['cases'])==6
tracks=sorted(set(c['capture']['fields'][2] for c in natural['cases']));assert tracks==list(range(4))
for c in natural['cases']:
 assert c['boundaries_identical'] and c['selector_entries_identical'] and c['event_final_identical'] and c['stock_regions_identical']
 assert not any(r['new_faults'] for r in c['runs'])
 assert hashlib.sha256(Path(c['capture']['path']).read_bytes()).hexdigest()==c['capture']['sha256']
for c in fixture['cases']:
 assert c['passed'] and c['stock']['stock_region_hashes']==c['helpers']['stock_region_hashes']
 assert not c['stock']['new_faults'] and not c['helpers']['new_faults']
assert fixture['cases'][0]['stock_note']==57 and fixture['cases'][0]['helper_note']==56
assert all(c['stock_note']==c['helper_note']==57 for c in fixture['cases'][1:])
selector_returns=[next(p['regs']['D0'] for p in c['runs'][0]['boundaries'] if p['pc']=='0x4009e694') for c in natural['cases']]
hashes={}
for name,path,expected in [('OS1.44','inputs/Digitone_and_Digitone_Keys_OS1.44.syx','d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'),('OS1.42 main','work/section-3.bin','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'),('OS1.44 helper image','work/os144/packed-context-overlay.bin','0c5d58bf72828102b6f1fe19277e633ef97503fdcb727fd2a5f728ded2a8e299')]:
 hashes[name]=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert hashes[name]==expected
summary={'passed':True,'firmware_modified':False,'startup_hook_installed':False,'paired_cases':14,'bounded_replays':28,'stock_derived_states':8,'tracks':tracks,'actual_selector_return_values':selector_returns,'positive_fixture':{'context_word':'0x800040bd','raw_scale':0,'root':61,'track':2,'stock_pitch':57,'helper_pitch':56,'other_pitch_boundary_registers_status_stack_event_match':True,'final_boundary_register_differences':fixture['cases'][0]['final_boundary_register_differences']},'fallback_modes':[c['fault'] for c in fixture['cases'][1:]],'stock_regions_checked':['event_pool','physical_cache','selected_records','acceptance_cache','selection_gates','caller_globals'],'hashes_after':hashes,'limits':['Replay starts at 0x4009e668 inside the stock render caller using captured guest registers/stack/memory and stops before common event release at 0x4009d7d8.','Snapshots omit host timer/DMA/scheduler components for these bounded replays; no asynchronous device-state continuity or physical timing proof.','The helper header is explicitly initialized; candidate metadata is seeded from the captured active pattern. Producer/allocator/copy hooks are not connected in these replays.','The non-chromatic sidecar fixture changes context only, without modifying event/selection fields. It tests intended pitch behavior, not natural context capture or old-scale retention across replacement.','Eight natural states cover observed branches and all four tracks, not every selector path, allocation failure, nested callback or concurrent transition.','Stock region hashes do not compare all RAM, DSP packets or final audio. No reserved-region ownership or cache-coherence certification.'],'next_step':'Connect producer capture and allocation/copy bookkeeping with these caller/pitch hooks in a PC-only session, then compare continuous stock/helper playback, sustain, cancellation and confirmed pattern handoff. Keep startup installation separate.'}
Path('outputs/Digitone-OS1.44-real-caller-summary.json').write_text(json.dumps(summary,indent=2))
doc='''# OS 1.44 actual selector and caller with context helpers

The actual changed stock selector and caller pass the bounded PC replay checks with the 1.44 helpers. Fourteen paired cases (28 replays) cover eight stock-generated states, one non-chromatic context fixture and five invalid-context controls. The firmware and helper image hashes remain unchanged. No startup hook was installed.

## Stock-derived execution

Eight guest snapshots were captured at `0x4009e668` during a clean stock session with queued notes, MIDI sustain, a confirmed pattern change and fresh receiving notes. They cover tracks 0–3, event types 0 and 1, descriptor-backed queued states and live MIDI states before/after replacement. Registers, the existing caller stack and guest memory are captured; branch results are not supplied by the test.

Each snapshot is replayed twice from the same state: once with stock call sites, once with temporary PC hooks for before/after selection, caller commit and pitch. Both execute the actual selector at `0x40097a94` and stop at the common release boundary `0x4009d7d8`.

For all eight natural cases:

- Selector return at `0x4009e694`, commit continuation when reached at `0x4009e738`, pitch continuation at `0x4009e890` and the final boundary match in registers, status, 64 bytes of current caller stack and original event bytes.
- Selector entries and the original event's final bytes match. Actual selector return values include a successful result of 1 and seven results of 0; the successful state reaches context commit, retained-context read and quantization.
- Final hashes match for the complete 128-event pool, four physical-cache slots, selected-note records, acceptance cache, selection gates and caller globals.
- The helper code remains intact and neither replay records a newly unmapped access.

The natural context words are chromatic. These equal-output cases verify caller compatibility, not a musical pitch change.

## Positive context and fallback

The successful stock-generated state is replayed with sidecar word `0x800040bd`: track 2, root 61, raw scale 0 (Ionian). This explicitly changes metadata only; the stock event and selection fields remain unchanged. The actual selector and caller still execute.

Stock note 57 becomes 56 at the helper pitch boundary, matching the independently extracted 1.44 scale oracle and downward tie rule. Selector and commit boundaries are identical. At pitch output, all registers other than D6, status, stack and event bytes match. D6 holds the expected fixed-point note. Checked stock memory regions and final release-boundary registers also match. DSP/audio output is not compared here.

Invalid magic, version, size, ready flag and a null owner pointer each fall back to stock note 57. Their observed caller boundaries match stock and quantization is not entered.

## Scope and next step

This closes the specific gap left by the previous entry/return-only tests: the changed selector now runs with the helpers around its real caller. It is still a bounded guest-state replay. Host timer, DMA and scheduler components are not restored for the slice, and no asynchronous transition or physical timing claim follows.

The private header and candidate metadata are explicit fixtures. Producer capture, allocation clearing and raw-copy bookkeeping are not yet connected in a continuously running 1.44 session. No eligible old-pattern note retaining scale across replacement, full reserved-memory ownership, cache coherence or startup installation is established here.

Next, connect those producer/allocation/copy paths with the verified caller/pitch hooks in a PC-only session and repeat continuous stock/helper playback, sustain, cancellation and a confirmed handoff. Keep startup installation separate until those checks pass.

Evidence files beside this report: `Digitone-OS1.44-caller-state-capture.json`, `Digitone-OS1.44-real-selector-caller.json`, `Digitone-OS1.44-real-selector-context.json`, and `Digitone-OS1.44-real-caller-summary.json`.
'''
Path('outputs/Digitone-OS1.44-real-selector-caller.md').write_text(doc)
print('PASS 14 paired actual selector/caller cases, including 57->56 and five fallback controls; no firmware/startup mutation.')
