import json,hashlib
from pathlib import Path
def read(scenario,mode):return json.loads(Path('outputs/Digitone-OS1.44-continuous-'+scenario+'-'+mode+'.json').read_text())
summary={'firmware_modified':False,'startup_hook_installed':False,'functional_checks_passed':True,'cases':[],'physical_timing_verified':False,'audio_equivalence_verified':False}
for scenario in ['ordinary','early-scale']:
 a,b=read(scenario,'stock'),read(scenario,'helpers')
 for r in [a,b]:
  assert r['failure'] is None and all(r['checks'].values()) and all(r['storage_checks'].values())
  assert r['firmware_sha256_after']=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
  marks={x['label']:x for x in r['marks']}
  old=marks['sustained waiting for handoff'];new=marks['confirmed handoff or bounded failure'];released=marks['sustain release settled']
  assert old['backing']!=new['backing'] and old['backing_hash']!=new['backing_hash']
  assert old['sustain_flags']==new['sustain_flags']!='0000000000000000' and old['sustain_lists']==new['sustain_lists']
  assert released['sustain_flags']=='0000000000000000' and all(p=='0x0' for p in released['sustain_lists'])
  f=r['delayed_queue_fixture'];life=[e for e in r['events'] if e.get('event')==f['event'] and e.get('generation')==f['generation']]
  assert any(e['kind']=='queued_event_released' for e in life) and not any(e['kind'] in ['acceptance','pitch'] for e in life)
 assert a['snapshot_sha256']==b['snapshot_sha256']
 assert [x[1] for x in a['inputs']]==[x[1] for x in b['inputs']]
 assert [x['bytes'] for x in a['midi_deliveries']]==[x['bytes'] for x in b['midi_deliveries']]
 assert all(c['matches'] for c in b['capture_checks'] if c['actual'] is not None)
 hits=b['helper_hits'];assert all(hits.get(k,0)>0 for k in ['producer_capture','allocate_clear','copy','before','after','caller_commit','pitch_hook'])
 qchecks=[]
 for q in b['quantizer_calls']:
  # A3 inside quantize is the helper's cached-selection scratch pointer,
  # not the original caller event. Resolve identity at the observed entry.
  context_track=(int(q['word'],16)>>13)&3
  entries=[e for e in b['events'] if e['kind']=='pitch' and e['ms']<=q['ms'] and e['fields'][2]==context_track and e['coarse_pitch']==q['note']]
  assert entries and q['ms']-entries[-1]['ms']<1 and entries[-1]['coarse_pitch']==q['note']
  entry=entries[-1]
  candidates=[p for p in b['pitch_outputs'] if p['event']==entry['event'] and p['generation']==entry['generation'] and q['ms']<=p['ms']<=q['ms']+1]
  assert candidates and candidates[0]['fixed_pitch']==q['expected']<<16,(q,candidates)
  qchecks.append({'ms':q['ms'],'event':entry['event'],'generation':entry['generation'],'helper_cached_selection_A3':q['event'],'word':q['word'],'input':q['note'],'output':candidates[0]['fixed_pitch']>>16,'oracle_match':True,'event_fields':candidates[0]['fields']})
 same_notes=[p['fixed_pitch'] for p in a['pitch_outputs']]==[p['fixed_pitch'] for p in b['pitch_outputs']]
 if scenario=='ordinary':assert same_notes
 case={'scenario':scenario,'stock_duration_ms':a['marks'][-1]['ms'],'helper_duration_ms':b['marks'][-1]['ms'],'snapshot_sha256':a['snapshot_sha256'],'panel_actions_same_order':True,'MIDI_bytes_same_order':True,'maximum_panel_action_time_difference_ms':max(abs(x[0]-y[0]) for x,y in zip(a['inputs'],b['inputs'])),'helper_hits':hits,'captures_checked':len(b['capture_checks']),'quantizer_checks':qchecks,'captured_source_note_cancelled':True,'sustain_preserved_and_released':True,'playing_handoff_confirmed':True,'stock_and_helper_pitch_sequences_equal':same_notes,'audio':{'stock_bytes':a['audio_bytes'],'helper_bytes':b['audio_bytes'],'stock_sha256':a['audio_sha256'],'helper_sha256':b['audio_sha256'],'equal':a['audio_sha256']==b['audio_sha256']},'storage_checks':b['storage_checks']}
 if scenario=='early-scale':
  assert b['allocation_clear_checks']==1357 and not b.get('allocation_clear_failures')
  assert len(b['copy_checks'])==2 and all(c['matches'] and c['bytes']==72 and c['expected']!=0 for c in b['copy_checks'])
  case['allocation_clear_checks']=b['allocation_clear_checks'];case['copy_checks']=b['copy_checks']
  release=b['delayed_release_observed'];assert release['fields'][3]==0xffffffff and release['return_to']=='0x4009d7e4';case['cancelled_release']=release
  write=next(e for e in b['events'] if e['kind']=='pattern_pointer_write' and e['ms']>1000)
  post=[q for q in qchecks if q['ms']>write['ms'] and q['word']=='0x800040bd']
  assert post
  old=post[0];assert old['input']==69 and old['output']==68 and old['event_fields'][2]==2 and old['event_fields'][14]!=0 and old['event_fields'][16]!=0 and old['event_fields'][10]&(1<<19)
  rows={x['raw_scale']:x['pitch_classes'] for x in json.loads(Path('outputs/Digitone-OS1.44-scale-map.json').read_text())['scales']}
  receiving=min((n for n in range(128) if (n-59)%12 in rows[5]),key=lambda n:(abs(n-69),n));assert receiving==69
  case['retained_cached_replay']={'handoff_ms':write['ms'],'replay_ms':old['ms'],'event':old['event'],'generation':old['generation'],'helper_cached_selection_A3':old['helper_cached_selection_A3'],'track':2,'event_type':old['event_fields'][0],'descriptor':hex(old['event_fields'][14]),'selected_identity':old['event_fields'][16],'context_word':old['word'],'source_root':61,'source_raw_scale':0,'receiving_root':59,'receiving_raw_scale':5,'input_note':69,'actual_source_scale_output':68,'receiving_scale_would_output':69,'notes_cancelled_by_stock_are_not_reactivated':True}
 summary['cases'].append(case)
summary['limits']=['Code/header installation is a post-boot PC fixture; source/receiving root/scale fields are explicit fixtures before selection. Event eligibility and metadata are produced by stock code and installed helpers.','Instruction-paced functional sessions omit calibrated memory/cache/DMA timing. Storage guards cover these finite runs only.','Controls share a snapshot, action order and MIDI content; realized action times differ slightly. Ordinary pitch sequences match, but audio hashes differ and the cause is not isolated.','The first_copy wrapper is installed but not entered in these runs; its prior isolated stock-ABI checks remain its current evidence.','The observed old-scale retention is eligible cached type-1 replay, not a surviving delayed type-0 queued note. The delayed type-0 note is cancelled.','Allocation/copy failures, longer heavy playback, startup/reset scheduling ownership, physical cache coherence and complete RAM ownership remain unverified.']
summary['excluded_nonchromatic_control']='The late scale-stock run set root/scale after initial candidate generation; it is not used as evidence of captured non-chromatic context.'
summary['next_step']='Isolate the ordinary audio difference with tighter input/phase controls, then repeat 1.44 render/DMA timing tests. Exercise the first-copy entry in continuous execution before treating copy-path coverage as complete; startup installation remains separate.'
for path,expected in [('work/os144/packed-context-overlay.bin','0c5d58bf72828102b6f1fe19277e633ef97503fdcb727fd2a5f728ded2a8e299'),('work/section-3.bin','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')]:assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
Path('outputs/Digitone-OS1.44-continuous-hook-summary.json').write_text(json.dumps(summary,indent=2))
retained=summary['cases'][1]['retained_cached_replay']
doc=f'''# OS 1.44 continuous PC hook integration

The producer, allocation, copy and caller/pitch hooks are connected in PC RAM. Two stock/helper pairs pass the functional playback, sustain, cancellation and confirmed pattern-handoff checks. Firmware remains unchanged and startup installation is not implemented. Audio equivalence and physical timing are not established.

## Execution and context handling

Both pairs start from the same fresh stock 1.44 snapshot and execute about 6.085 emulated seconds without resetting through the playing handoff. They use the same panel-action order and MIDI bytes; realized action times differ slightly because this engine advances instruction-paced time.

All seven hook sites are installed in the helper sessions. Producer capture, allocator clearing, normal raw copy, before/after selector, caller commit and pitch execute. The separate first-copy wrapper is not entered in these scenarios; it retains only its previous isolated ABI evidence.

The non-chromatic pair sets the source pattern's root/raw scale to 61/0 and receiving pattern's to 59/5 **before** stopped pattern selection and note generation. These are explicit PC pattern-data fixtures. No event eligibility, selected identity or context word is injected. Helper metadata comes from the executed producer/copy/commit paths.

- Sixteen producer captures match the corresponding pattern's root/scale encoding.
- All 1,357 observed eligible allocation returns have a cleared context slot.
- Both observed 72-byte cache-to-pool copies propagate their nonzero context exactly.
- Eleven quantizer calls match an independent oracle built from the extracted 1.44 scale rows; their actual fixed-point pitch outputs agree.
- Code, unused reserved-region bytes and guards remain intact, with no unexpected writes to the watched region.

## Sustained and cancelled notes

In stock and helper runs, MIDI note-off leaves the sustained-note flag/list populated through the actual pattern replacement. Pedal release clears both, and a fresh receiving note reaches pitch output.

The delayed type-0 source note is still cancelled. With helpers installed, its `+0x0C` is `0xFFFFFFFF` at release and its return site is the same stock consumer cleanup path. It never reaches acceptance or pitch output for that allocation generation. Retained context does not reactivate it.

## Eligible cached replay after replacement

The receiving pattern is published at {retained['handoff_ms']:.6f} ms. At {retained['replay_ms']:.6f} ms, event `{retained['event']}` (generation {retained['generation']}) on track 2 reaches pitch output with a non-null descriptor, selected identity 1 and the stock eligibility flag set. Its cached-selection state is read through helper scratch pointer `{retained['helper_cached_selection_A3']}`. It uses retained word `0x800040bd`, captured for source root 61/raw scale 0. The event address is resolved from the original caller entry; A3 inside quantize has a different scratch role.

Its input note 69 becomes 68 under that source scale. The receiving root 59/raw scale 5 would leave it at 69. This demonstrates old-scale retention for this **eligible cached type-1 replay in the PC run**. It does not demonstrate survival of the separately delayed type-0 queued note.

## Audio and remaining coverage

The ordinary stock/helper pitch sequences match and both runs produce 1,168,256 audio bytes, but their audio hashes differ. That difference remains unexplained. Because realized input times also differ, these controls do not isolate its cause. Non-chromatic audio differences additionally include the intended pitch changes.

These finite sessions do not certify timing, cache coherence or exclusive reserved-memory ownership. Startup/bootstrap installation, reset shutdown ordering, allocation failures, all copy paths and longer voice-heavy playback remain outside this check. The late scale control that changed fields after candidate generation is excluded from the non-chromatic capture evidence.

Next, isolate the ordinary audio difference with tighter phase/input controls and repeat 1.44 render/DMA timing checks. Also exercise the first-copy route in continuous execution before treating copy coverage as complete. Keep startup installation separate.

Evidence: `Digitone-OS1.44-continuous-hook-summary.json` and the four `ordinary-stock`, `ordinary-helpers`, `early-scale-stock`, and `early-scale-helpers` continuous trace JSON files beside this report.
'''
Path('outputs/Digitone-OS1.44-continuous-hooks.md').write_text(doc)
print('PASS continuous functional integration, captured context/copy/clear, sustain/cancellation/handoff and retained eligible cached replay. Audio equivalence unresolved; first-copy path unobserved.')
