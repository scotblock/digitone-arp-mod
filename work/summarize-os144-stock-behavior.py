import json,hashlib,collections
from pathlib import Path
def load(name):return json.loads(Path('outputs/'+name+'.json').read_text())
startup=load('Digitone-OS1.44-stock-startup');combined=load('Digitone-OS1.44-stock-sustain-transition');delayed=load('Digitone-OS1.44-stock-delayed-queue');isolated=load('Digitone-OS1.44-stock-pattern-isolation')
expected='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
for r in [startup,combined,delayed,isolated]:assert r['failure'] is None and r['firmware_sha256_after']==expected
assert all(combined['checks'].values()) and all(delayed['checks'].values()) and isolated['actual_playing_handoff']
marks={m['label']:m for m in combined['marks']}
before=marks['sustained waiting for handoff'];after=marks['confirmed handoff or bounded failure'];released=marks['sustain release settled']
assert before['sustain_flags']==after['sustain_flags']!='0000000000000000'
assert before['sustain_lists']==after['sustain_lists'] and any(x!='0x0' for x in before['sustain_lists'])
assert released['sustain_flags']=='0000000000000000' and all(x=='0x0' for x in released['sustain_lists'])
writes=[e for e in combined['events'] if e['kind']=='pattern_pointer_write' and e['ms']>1000]
assert len(writes)==1
change=writes[0];assert change['backing']!=change['incoming'] and before['backing_hash']!=after['backing_hash']
accepted=[e for e in combined['events'] if e['kind']=='acceptance' and e.get('publication')]
pubs=[e for e in combined['events'] if e['kind']=='queue_publish']
slots=collections.Counter(e['event'] for e in pubs)
f=delayed['delayed_queue_fixture'];life=[e for e in delayed['events'] if e.get('event')==f['event'] and e.get('generation')==f['generation']]
assert any(e['kind']=='queued_event_released' for e in life)
assert not any(e['kind'] in ('acceptance','pitch') for e in life)
fresh_start=marks['fresh receiving note on']['ms']-21
fresh=[e for e in combined['events'] if e['kind']=='pitch' and fresh_start<=e['ms']<=marks['fresh receiving note off']['ms'] and e['coarse_pitch']==62]
assert fresh
sha=hashlib.sha256(Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx').read_bytes()).hexdigest();assert sha==expected
baseline_sha=hashlib.sha256(Path('work/section-3.bin').read_bytes()).hexdigest();assert baseline_sha=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'
summary={'firmware_modified':False,'custom_arp_hooks_installed':False,'functional_scenarios_verified':True,'full_certification':False,'firmware_sha256':sha,'baseline_142_main_unchanged':True,'startup_snapshot_sha256':startup['snapshot_sha256'],'combined':{'modeled_ms':marks['fresh note release settled']['ms'],'counts':combined['counts'],'published_events':len(pubs),'matching_publication_acceptances':len(accepted),'reused_published_slots':sum(n>1 for n in slots.values()),'producer_tracks':sorted(set(e['producer_track'] for e in combined['events'] if e['kind']=='producer')),'playing_pattern_change':{k:change[k] for k in ['ms','pc','backing','incoming']},'pending_at_change':len(change['pending_publications']),'sustain_preserved_through_change':True,'sustain_flag_and_list_cleared':True,'fresh_62_pitch_outputs':len(fresh),'naturally_cross_pattern_acceptances':len(combined['cross_pattern_acceptances'])},'delayed_note':{'fixture':f,'same_generation_lifetime':[{'kind':e['kind'],'ms':e['ms'],'backing':e.get('backing')} for e in life],'outcome':'Released after replacement without an observed acceptance or pitch call for this generation. Release decision branch not yet traced.','proof_of_eligible_old_note_pitch_across_replacement':False},'negative_handoff_controls':['Digitone-OS1.44-stock-behavior.json','Digitone-OS1.44-stock-handoff.json','Digitone-OS1.44-stock-pattern-request-debug.json'],'limits':['Finite stock functional scenarios, not exhaustive event-copy/remap or allocation-failure coverage.','Delayed timestamp is a PC-only fixture; it does not prove natural occurrence of that scheduling sequence.','Stock firmware has no custom root/scale metadata; this does not test retained scale context.','Earlier multi-input requests did not complete; their recurring transition_done probe is a sequencer callback, not completion evidence.','Instruction-paced emulator with float/bitmap/storage/ISA/device stand-ins, not a calibrated hardware timing or cache-coherence test.','Direct main-image startup; full loader-to-main inherited state not exercised.'],'next_step':'Trace the delayed note release decision and selector eligibility under 1.44, then update the PC hook contracts and replay verified scenarios before installing custom overlays.'}
Path('outputs/Digitone-OS1.44-stock-verification-summary.json').write_text(json.dumps(summary,indent=2))
text=f'''# Stock Digitone OS 1.44: PC behavior verification

The stock 1.44 engine boots to a settled interface and executes queue handling, MIDI sustain and an actual playing pattern change. These observed functional scenarios pass. Firmware files and the 1.42 main-program reference remain unchanged; no custom arp code was installed.

## Verified execution

The new baseline starts from the supplied 1.44 main program with a fresh emulated drive and snapshot, not a 1.42 snapshot. First boot settled at the engine's estimated 1,400M instruction mark. This uses the engine's direct main-image entry rather than the full firmware loader.

In the combined run, lasting {summary['combined']['modeled_ms']/1000:.3f} emulated seconds:

- {len(pubs):,} events reached the actual queue publisher. {len(accepted)} observed acceptance calls matched an earlier publication by address and allocation generation. {summary['combined']['reused_published_slots']} published slots were reused. Real producer calls were observed for all four track indices.
- MIDI CC64 set the sustain flag. Note-off left a retained note-list entry. That same flag and list entry persisted through actual replacement, then pedal release cleared both.
- The active pattern backing switched from `{change['backing']}` (pattern 2) to `{change['incoming']}` (pattern 1), at {change['ms']:.6f} ms, written by stock code at `{change['pc']}`. The receiving pattern's data hash differs. Six pending publications were observed at that boundary; this alone does not establish that a queued note survives it.
- A fresh MIDI note after replacement reached stock pitch output with pitch 62. The parser handled all injected MIDI bytes, and the engine did not halt.

The input-enable setting is a disclosed PC RAM fixture so the real DIN MIDI parser accepts the test bytes. Note handling, queue publication/consumption, pattern replacement and pedal handling execute stock instructions.

## Delayed queued note

A second run delays one actual stock-produced type-0 note by 96,000,000 queue timer ticks, changing only the publisher's timestamp argument in PC RAM. The event's fields and eligibility are not manufactured. It is `{f['event']}`, generation {f['generation']}, track {f['original_fields'][2]}, and has a non-null `+0x38` descriptor (`{hex(f['original_fields'][14])}`).

The event remains identifiable across replacement, but is released at {next(e['ms'] for e in life if e['kind']=='queued_event_released'):.6f} ms without reaching the instrumented acceptance or pitch point for that generation. This is **not** a successful old-note pitch replay. The exact release decision still needs tracing; do not infer its cause from the final release alone. The unmodified combined run also contains no matched publication/acceptance pair crossing pattern backings.

## Controls and limits

Earlier multi-input runs did not complete their playing pattern requests. Those negative traces are retained separately and excluded as handoff proof. A minimal stock panel sequence established a real playing transition; repeating it with MIDI sustain also succeeded. The recurring probe previously labeled `transition_done` is a sequencer callback and is not used as completion evidence. The pointer write and changed receiving data establish the observed replacement.

These are finite functional observations. Allocation failures, all copying/remap branches, naturally eligible delayed arp playback across replacement, and custom retained root/scale context are not exhaustively verified. Instruction pacing and engine float/bitmap, storage, device and ISA stand-ins remain in use. Physical cycle timing, DMA/cache coherence and reserved RAM ownership are not established by this run.

## Next step

Trace why the delayed stock note is released and check the changed selector's eligibility/list handling. Use that result to adapt the 1.44 PC hook contracts, then replay these successful scenarios with overlays. Keep custom hooks unconnected until those contracts are checked.

Evidence files beside this report: `Digitone-OS1.44-stock-startup.json`, `Digitone-OS1.44-stock-pattern-isolation.json`, `Digitone-OS1.44-stock-sustain-transition.json`, `Digitone-OS1.44-stock-delayed-queue.json`, and `Digitone-OS1.44-stock-verification-summary.json`.
'''
Path('outputs/Digitone-OS1.44-stock-verification.md').write_text(text)
print('PASS stock startup, queue generations, sustained-note retention/release, actual playing handoff and fresh receiving note. Delayed old note released; eligible replay remains unproven.')
