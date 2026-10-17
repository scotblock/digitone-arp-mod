"""Verify native panel -> write -> dirty -> guarded publication -> context."""
from pathlib import Path
import json,hashlib

folder=Path('outputs')
r=json.loads((folder/'Digitone-E08E-complete-panel-race-handoff.json').read_text())
assert r['passed'] and r['halted'] is None and not r['failure']
assert r['incoming_panel_edit_reached'] is True
assert all(r[k] is False for k in ['helpers_host_loaded','hooks_host_patched','M1_initializer_host_called','settings_host_written'])
assert r['MIDI_received']==r['MIDI_delivered']
e=r['events'];marks={x['label']:x for x in r['pattern_marks']}
A=marks['A01_live_edit']['data'];B=marks['incoming_UI_before_context']['data']
assert A!=B and marks['incoming_UI_before_context']['owner']==A
turn=next(x for x in e if x['kind']=='detailed_panel' and x['handler']=='0x47be6300' and x['phase']=='edit_incoming_before_context')
assert turn['view_tag']=='0x4d314352' and turn['data']==B and turn['owner']==A
boundary=[x for x in e if x['kind'].startswith('panel_boundary') and x['phase']=='edit_incoming_before_context']
assert [(x['kind'],x['callee']) for x in boundary]==[
    ('panel_boundary_enter','0x47be5900'),('panel_boundary_return','0x47be5900'),
    ('panel_boundary_enter','0x4014eff8'),('panel_boundary_return','0x4014eff8'),
    ('panel_boundary_enter','0x47be7000'),('panel_boundary_return','0x47be7000')]
write_enter,write_return,dirty_enter,dirty_return,publish_enter,publish_return=boundary
assert write_enter['word']==0xac94 and write_return['word']==0xacb2 and write_return['result']=='0x1'
assert write_enter['args'][1:]==['0x1','0x1','0x32']
assert dirty_return['stock_cache']=='0x0' and dirty_enter['stock_cache']!=dirty_return['stock_cache']
assert publish_enter['args']==[B,'0xacb2','0x1'] and publish_return['result']=='0x0'
assert all(x['owner']==A and x['config']==[1,3,50,0] for x in boundary)
context=next(x for x in e if x['kind']=='context_consume' and x['kit']==marks['incoming_edit_applied']['stock_kit'] and x['ms']>publish_return['ms'])
assert context['descriptor_word']==0xacb2 and context['owner']==A and context['config']==[1,3,50,0]
configs=[x for x in e if x['kind']=='configure_called' and publish_return['ms']<=x['ms']<=context['ms']]
assert len(configs)==1
cfg=configs[0]
assert cfg['ms']==context['ms'] and cfg['rate_index']==1 and cfg['gate_percent']==50 and cfg['owner']==B
assert not [x for x in e if x['kind']=='pending_settings_word' and publish_return['ms']<=x['ms']<context['ms']]
assert not [x for x in e if x['kind']=='configure_called' and publish_return['ms']<=x['ms']<context['ms']]
assert marks['incoming_edit_deferred']['word']==0xacb2 and marks['incoming_edit_deferred']['config']==[1,3,50,0]
assert marks['incoming_edit_applied']['config']==[1,1,50,0]
assert marks['A02_live_edit']['word']==0xacd0 and marks['A02_live_edit']['config']==[1,1,80,0]
assert marks['saved_A01_return']['word']==0xadb2 and marks['saved_A02_return']['word']==0xacd0

parser=Path('work/verify-E08C-packaged-controls.py').read_text()
a=parser.index('def packets(events):');z=parser.index('\nactive, ons, offs',a)
exec(compile(parser[a:z],'independent-serial-MIDI-parser','exec'))
active={};ons=0;offs=0
for x in packets(r['wire']):
    key=(x['status']&15,x['note'])
    if x['status']&0xf0==0x90 and x['velocity']:
        assert key not in active
        active[key]=x;ons+=1
    else:
        assert key in active
        active.pop(key);offs+=1
assert not active and ons==offs and ons>20
layout=json.loads((folder/'Digitone-E08E-PC-path-layout.json').read_text())
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(layout['candidate'])==r['candidate_sha256']==layout['candidate_sha256']
assert digest('work/os144/E08C-PC-path-candidate.syx')=='081c592e16bb8cb32b0b4c0ede6f0f10bc8dec95c783a50a7ee259d8d4ee6da6'
assert digest(folder/'Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx')=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
result={'PC_only':True,'passed':True,'hardware_ready':False,'candidate_firmware_changed':False,
    'candidate_sha256':r['candidate_sha256'],'complete_native_panel_race_witnessed':True,
    'native_panel_write_ms':write_return['ms'],'native_dirty_notification_return_ms':dirty_return['ms'],
    'different_owner_publication_refused_ms':publish_return['ms'],'context_consumed_ms':context['ms'],
    'edited_settings_applied_ms':cfg['ms'],'deferred_for_ms':context['ms']-publish_return['ms'],
    'premature_configuration_calls':0,'old_owner':A,'incoming_owner':B,
    'old_playback_config':[1,3,50],'incoming_edited_config':[1,1,50],
    'subsequent_active_owner_edit_accepted':True,'separate_in_memory_pattern_values_preserved':True,
    'note_ons':ons,'matched_note_offs':offs,'hanging_notes':0,'E07_and_E08C_unchanged':True,
    'cause_of_earlier_non_witness':'The existing custom page remained active. Reopening disturbed it, and the 30 ms observation ended before delayed native encoder dispatch. The successful attempt left the page open and observed for 80 ms.',
    'limits':['This is a witnessed native execution sequence under the PC engine and inherited loader-derived state, not every possible interrupt interleaving or physical timing.',
              'Dirty notification and in-memory retention were observed; this test does not prove on-disk project save/reload.',
              'Same-address record reuse, queued-old-note replacement, physical RAM/DMA ownership and cache/timing remain separate checks.']}
(folder/'Digitone-E08E-complete-panel-race-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
