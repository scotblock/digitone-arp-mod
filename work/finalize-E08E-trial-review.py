"""Freeze a reviewable experimental artifact only after required PC checks."""
from pathlib import Path
import json,hashlib
out=Path('outputs');read=lambda n:json.loads((out/f'Digitone-E08E-{n}.json').read_text())
names=['stop-guard-contracts','owner-guard-contracts','PC-copier-initialization','packed-loader',
       'PC-startup-comparison','pattern-settings','running-pattern-handoff','trial-note-lifecycle-results',
       'complete-panel-race-results','project-readiness-results','trial-startup-delta',
       'startup-DIN-checks','PC-container-verification','reset-refusal']
reports={n:read(n) for n in names}
assert all(r['passed'] and not r.get('failure') for r in reports.values())
cfg=read('PC-path-layout');digest=cfg['candidate_sha256']
assert digest=='74219ea223999ae190f5c935973b96bf67eea60148416a1009565af6f48dd3a3'
raw=Path(cfg['candidate']).read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)==digest
for name,key in [('packed-loader','candidate_sha256'),('pattern-settings','candidate_sha256'),
                 ('running-pattern-handoff','candidate_sha256'),('trial-note-lifecycle-results','candidate_sha256'),
                 ('complete-panel-race-results','candidate_sha256'),('startup-DIN-checks','image_sha256'),
                 ('PC-container-verification','sha256')]:assert reports[name][key]==digest,name

source=Path('work/verify-E08C-packaged-controls.py').read_text();a=source.index('def packets(events):');z=source.index('\nactive, ons, offs',a)
exec(compile(source[a:z],'independent-MIDI-parser','exec'))
r=reports['running-pattern-handoff'];active={};on=off=0
for e in packets(r['wire']):
    key=(e['status']&15,e['note'])
    if e['status']&0xf0==0x90 and e['velocity']:
        assert key not in active;active[key]=e;on+=1
    else:assert key in active;active.pop(key);off+=1
assert not active and on==off
events=[e for e in r['events'] if e['phase']=='handoff_A02']
context=next(e for e in events if e['kind']=='context_consume' and e['descriptor_word']==0xac94)
configure=next(e for e in events if e['kind']=='configure_called')
assert context['ms']==configure['ms'] and configure['owner']==context['data']
assert r['MIDI_received']==r['MIDI_delivered']
assert all(r[k] is False for k in ['helpers_host_loaded','hooks_host_patched','M1_initializer_host_called','settings_host_written'])
assert len(reports['reset-refusal']['cases'])==9 and all(x['balanced_return'] and not x['writes'] for x in reports['reset-refusal']['cases'])
stock=out/'stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx'
assert sha(stock.read_bytes())=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
assert sha((out/'Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes())=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
path=out/'Digitone_OS1.44E08E_M1_ARP_PC_ONLY.syx'
assert not path.exists() or path.read_bytes()==raw
path.write_bytes(raw);assert sha(path.read_bytes())==digest
result={'PC_only':True,'PC_acceptance_checks_passed':True,'hardware_ready':False,'hardware_tested':False,
 'device_updated':False,'trial_proposal':'One user-operated M1-only experimental boot/playback trial, subject to agreement; not general-use certification.',
 'candidate':str(path.resolve()),'candidate_sha256':digest,'file_bytes':len(raw),
 'stock_recovery':str(stock.resolve()),'stock_recovery_sha256':sha(stock.read_bytes()),
 'changes_since_E08D':['Stop now quiesces M1 at the actual outer stock MIDI-task Stop command before stock drains outgoing notes.',
                       'Applying OFF clears M1 generation and membership, retaining a busy descriptor for native retirement.'],
 'additional_state_bytes_since_E08D':0,'additional_copy_bytes_since_E08D':0,
 'handoff_note_pairs':on,'lifecycle_note_pairs':reports['trial-note-lifecycle-results']['note_ons'],
 'panel_race_note_pairs':reports['complete-panel-race-results']['note_ons'],
 'native_project_save_reload':True,'same_address_quiescent_reload':True,
 'startup_receiver_valid_and_three_rejections':True,'strict_native_regions':reports['trial-startup-delta']['native_executable_regions_checked'],
 'checks':names,'preserved_working_E07_and_stock':True,
 'residual_risks':['Physical execution/cache coherence and DDR/DMA ownership of the extended reserved interval have not been measured.',
                   'Real-time audio/MIDI timing under voice-heavy workloads is not established.',
                   'Live project-load/input overlap, all in-place record reuse, queued-old-note replacement and arbitrary warm/copier/exception paths are not certified.',
                   'M2-M4 arps are not implemented. Simultaneous synth/MIDI arps, shared-channel ownership and congested MIDI output need broader coverage.',
                   'The latest continuous playback runs use live MIDI input; internal sequencer-chord playback has not been repeated on this final package.',
                   'Boot failure, hung notes/audio faults, project data loss and unsuccessful recovery remain possible experimental-firmware risks.']}
(out/'Digitone-E08E-hardware-trial-review-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['PC_acceptance_checks_passed','hardware_ready','candidate','candidate_sha256','handoff_note_pairs','lifecycle_note_pairs','panel_race_note_pairs']},indent=2))
