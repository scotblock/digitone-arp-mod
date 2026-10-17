from pathlib import Path
import json,hashlib
folder=Path('outputs')
read=lambda name:json.loads((folder/name).read_text())
prep=read('Digitone-E08C-pattern-settings.json')
run=read('Digitone-E08C-running-pattern-handoff.json')
control=read('Digitone-E08C-order-control-handoff.json')
copy=read('Digitone-E08C-native-copy-clear.json')
reset=read('Digitone-E08C-reset-refusal.json')
assert all(r['passed'] and not r.get('failure') for r in [prep,run,control,copy,reset])
assert prep['two_pattern_settings_isolated']
assert run['A01_context_applied'] and run['A02_context_applied']
assert run['MIDI_received']==run['MIDI_delivered']
assert control['MIDI_received']==control['MIDI_delivered']
assert run['helpers_host_loaded'] is False and control['helpers_host_loaded'] is True

# The real serial stream, including channel changes, is parsed independently
# from the native model's scheduling decisions.
text=Path('work/verify-E08C-packaged-controls.py').read_text()
a=text.index('def packets(events):');z=text.index('\nactive, ons, offs',a)
exec(compile(text[a:z],'MIDI-byte-stream-parser','exec'))
def notes(r):
    events=packets(r['wire']);active={};ons=[];offs=[]
    for e in events:
        key=(e['status']&15,e['note'])
        if e['status']&0xf0==0x90 and e['velocity']:
            assert key not in active,(key,e)
            active[key]=e;ons.append(e)
        else:
            assert key in active,(key,e)
            start=active.pop(key);offs.append({**e,'gate_ms':e['ms']-start['ms']})
    assert not active and len(ons)==len(offs)
    # Every output note is from the test chord; output changes from MIDI ch1
    # to ch6 in A02, then returns to ch1. No desired ch16 value is assumed.
    assert {e['note'] for e in ons}=={60,64,67}
    for phases in [{'A01_held','request_A02','handoff_A02'}, {'A01_fresh'}]:
        seq=[e['note'] for e in ons if e['phase'] in phases]
        assert seq and seq==([60,64,67]*((len(seq)+2)//3))[:len(seq)],seq
    marks={m['label']:m for m in r['pattern_marks']}
    assert marks['A02_request']['word']==0xadd0
    assert marks['A02_completed']['word']==0xac94
    assert marks['A01_completed']['word']==0xadd0
    assert marks['A02_held_playback']['held'][0:3]==[1,1,3]
    assert marks['A02_released']['held'][0]==0 and marks['A02_released']['held'][2:]==[0,0]
    assert marks['A01_fresh_released']['held'][0]==0 and marks['A01_fresh_released']['held'][2:]==[0,0]
    return ons,offs
ons,offs=notes(run);control_ons,control_offs=notes(control)

def ordering(r,word,phase):
    events=[e for e in r['events'] if e['phase']==phase]
    context=next(e for e in events if e['kind']=='context_consume' and e['descriptor_word']==word)
    cfg=next(e for e in events if e['kind']=='configure_called')
    publishers=[e for e in events if e['kind']=='pending_settings_word']
    return {'context_ms':context['ms'],'first_configure_ms':cfg['ms'],
            'configure_lead_ms':context['ms']-cfg['ms'],
            'first_publisher_pc':publishers[0]['writer']}
baseline_order=ordering(run,0xac94,'handoff_A02')
guard_order=ordering(control,0xac94,'handoff_A02')
assert baseline_order['configure_lead_ms']>100
assert abs(guard_order['configure_lead_ms'])<.1
assert baseline_order['first_publisher_pc']!=guard_order['first_publisher_pc']

# Align at actual receiving MIDI context consumption. The baseline's extended
# gap before it differs from the control that leaves settings with the context.
def near_context(ons,order):
    return [{'relative_ms':e['ms']-order['context_ms'],'note':e['note'],'channel':(e['status']&15)+1}
            for e in ons if -200<e['ms']-order['context_ms']<350]
base_near=near_context(ons,baseline_order);guard_near=near_context(control_ons,guard_order)
base_pre=[e for e in base_near if -100<e['relative_ms']<0]
guard_pre=[e for e in guard_near if -100<e['relative_ms']<0]
assert len(guard_pre)>len(base_pre),(base_near,guard_near)

cm={r['label']:r for r in copy['pattern_marks']}
assert copy['paste_carries_extension'] and copy['undo_paste_restores_extension'] and copy['A01_unaffected']
assert cm['A02_before_paste']['word']==0xac94 and cm['A02_after_paste']['word']==0xadd0
assert cm['A02_undo_paste']['word']==0xac94
assert cm['A02_paste_again']['B_record']==cm['A02_after_clear']['B_record']==cm['A02_undo_clear']['B_record']
assert len(reset['cases'])==9 and all(r['passed'] and not r['writes'] and r['balanced_return'] for r in reset['cases'])
layout=read('Digitone-E08C-PC-path-layout.json')
assert hashlib.sha256(Path(layout['candidate']).read_bytes()).hexdigest()==layout['candidate_sha256']
e07=folder/'Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx'
assert hashlib.sha256(e07.read_bytes()).hexdigest()=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
result={'PC_only':True,'checks_completed':True,'hardware_ready':False,'new_firmware_released':False,
        'two_pattern_settings_isolated':True,'running_native_contexts_observed':True,
        'held_note_handoff_pairs':len(ons),'control_handoff_pairs':len(control_ons),'no_hanging_notes':True,
        'copy_paste_and_undo_preserve_extension':True,'sequence_clear_and_undo_preserve_MIDI_record':True,
        'native_reset_refusal_cases':9,'M1_storage_unchanged_on_refusal':True,
        'handoff_ordering_certified':False,'baseline_order':baseline_order,'PC_overlay_control_order':guard_order,
        'baseline_notes_near_context':base_near,'control_notes_near_context':guard_near,
        'queued_old_note_coverage':False,'E08C_package_unchanged_sha256':layout['candidate_sha256'],
        'limits':['The baseline running handoff test exposes settings application before the native receiving MIDI context. It is not a full handoff pass.',
                  'The separate PC control suppresses automatic binding publication during playback. It is host-loaded code and is not integrated or approved as a complete fix.',
                  'Live panel-edit ownership and a naturally queued old note crossing replacement remain unproven.',
                  'The inherited transition_done probe fires periodically. Its label does not establish completion; actual context consumption and changed backing/data pointers are the witnesses used here.',
                  'The attempted channel-16 setup did not establish channel 16. Actual native outputs are channels 1 and 6; all note-offs are checked against their actual channel.',
                  'Reset calls are stopped, isolated native entry calls with admission fixtures, not concurrent UI/input reset tests.',
                  'Physical RAM, cache and real-time timing remain unverified.']}
(folder/'Digitone-E08C-pattern-copy-reset-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
