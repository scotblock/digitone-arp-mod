"""Independent ownership/order/MIDI checks for the internal PC candidate."""
from pathlib import Path
import json,hashlib

folder=Path('outputs')
read=lambda n:json.loads((folder/f'Digitone-E08D-{n}.json').read_text())
run=read('running-pattern-handoff');live=read('live-edit-handoff')
prep=read('pattern-settings');unit=read('owner-guard-contracts')
copy=read('native-copy-clear');reset=read('reset-refusal')
loader=read('packed-loader');startup=read('PC-startup-comparison');copier=read('PC-copier-initialization')
layout=read('PC-path-layout')
panel_race=read('complete-panel-race-results')
assert panel_race['passed'] and panel_race['complete_native_panel_race_witnessed']
assert all(r['passed'] and not r.get('failure') for r in [run,live,prep,unit,copy,reset,loader,startup,copier])
text=Path('work/verify-E08C-packaged-controls.py').read_text()
a=text.index('def packets(events):');z=text.index('\nactive, ons, offs',a)
exec(compile(text[a:z],'independent-MIDI-parser','exec'))

def playback(r):
    active={};ons=[];offs=[]
    for e in packets(r['wire']):
        key=(e['status']&15,e['note'])
        if e['status']&0xf0==0x90 and e['velocity']:
            assert key not in active,(key,e)
            active[key]=e;ons.append(e)
        else:
            assert key in active,(key,e)
            start=active.pop(key);offs.append({**e,'gate_ms':e['ms']-start['ms']})
    assert not active and len(ons)==len(offs)
    assert {e['note'] for e in ons}=={60,64,67}
    assert r['MIDI_received']==r['MIDI_delivered'] and r['halted'] is None
    for key in ['helpers_host_loaded','hooks_host_patched','M1_initializer_host_called','settings_host_written']:
        assert r[key] is False,key
    return {'note_ons':len(ons),'note_offs':len(offs),'hanging_notes':0,
            'channels':sorted({(e['status']&15)+1 for e in ons})}

def order(word,phase):
    e=[e for e in run['events'] if e['phase']==phase]
    c=next(x for x in e if x['kind']=='context_consume' and x['descriptor_word']==word)
    cfg=next(x for x in e if x['kind']=='configure_called')
    applied=next(x for x in e if x['kind']=='context_applied' and x['data']==c['data'])
    assert abs(cfg['ms']-c['ms'])<.01
    assert cfg['owner']==c['data']==applied['owner']
    assert cfg['rate_index']==(word>>7)&7 and cfg['gate_percent']==word&127
    assert c['owner']!=applied['owner']
    early=[x for x in e if x['ms']<c['ms'] and x.get('data')==c['data']]
    assert early
    assert all(x['owner']==c['owner'] and x['config'][:3]==c['config'][:3] for x in early)
    return {'context_ms':c['ms'],'first_configuration_ms':cfg['ms'],
            'configuration_lead_ms':c['ms']-cfg['ms'],
            'observed_UI_lookahead_ms':c['ms']-early[0]['ms'],
            'old_owner':c['owner'],'receiving_owner':applied['owner']}

handoff=order(0xac94,'handoff_A02');back=order(0xadd0,'handoff_A01')
marks={r['label']:r for r in live['pattern_marks']}
assert marks['A01_live_edit']['config']==[1,3,50,0]
assert marks['A01_live_edit']['word']==0xadb2
assert marks['incoming_UI_before_context']['owner']==marks['A01_live_edit']['data']
assert marks['incoming_edit_deferred']['config']==[1,3,50,0]
assert marks['A02_live_edit']['config'][:2]==[1,1]
assert marks['A02_live_edit']['owner']==marks['A02_live_edit']['data']
assert marks['saved_A01_return']['word']==0xadb2
assert marks['saved_A02_return']['word']==marks['A02_live_edit']['word']
assert copy['paste_carries_extension'] and copy['undo_paste_restores_extension'] and copy['A01_unaffected']
assert len(reset['cases'])==9 and all(x['balanced_return'] and not x['writes'] for x in reset['cases'])
assert len(unit['checks'])==12 and unit['strict_ColdFire_checked']
assert loader['main_matches'] and not loader['flash_writes']
assert layout['payload_bytes']==32256 and layout['state_bytes']==344
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(layout['candidate'])==layout['candidate_sha256']==loader['candidate_sha256']==run['candidate_sha256']==live['candidate_sha256']
assert panel_race['candidate_sha256']==layout['candidate_sha256']
assert digest('work/os144/E08C-PC-path-candidate.syx')=='081c592e16bb8cb32b0b4c0ede6f0f10bc8dec95c783a50a7ee259d8d4ee6da6'
assert digest(folder/'Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx')=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
result={'PC_only':True,'passed':True,'hardware_ready':False,'released_firmware':False,
    'candidate_sha256':layout['candidate_sha256'],'E07_and_E08C_unchanged':True,
    'native_contract_groups':len(unit['checks']),'native_reset_refusals':len(reset['cases']),
    'state_bytes':344,'additional_owner_bytes':8,'arena_moved':False,'copied_payload_bytes':32256,
    'loader_startup_copy_checked':True,'native_copy_paste_undo_checked':True,
    'handoff_to_A02':handoff,'handoff_to_A01':back,
    'continuous_handoff_MIDI':playback(run),'continuous_live_edit_MIDI':playback(live),
    'current_owner_panel_edits_A_and_B':True,
    'incoming_bank_edit_guard_native_fixture_checked':True,
    'initial_UI_test_reached_incoming_edit':live['incoming_panel_edit_reached'],
    'incoming_bank_edit_reached_in_continuous_UI_test':panel_race['complete_native_panel_race_witnessed'],
    'complete_panel_race':panel_race,
    'limits':['A complete native panel edit/dirty notification/refused early publication/consumed-context application is now witnessed in the separate panel-race test. This does not establish every interrupt interleaving or hardware timing.',
              'Stopped native reset-entry tests use explicit admission fixtures, not asynchronous reset or exception evidence.',
              'The new retained pointer is an identity only. This is not a global proof against same-address reuse or every in-place record replacement.',
              'A queued old note crossing pattern replacement, continuous project save/reload with these new guards, and M2-M4 remain untested here.',
              'Physical RAM/DMA ownership, cache coherence and real-time timing remain unverified.']}
(folder/'Digitone-E08D-owner-guard-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
