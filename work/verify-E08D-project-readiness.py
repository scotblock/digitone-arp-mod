from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E08D-packaged-project-controls.json').read_text())
assert r['passed'] and r['halted'] is None and not r.get('failure')
assert r['helpers_host_loaded'] is False and r['hooks_host_patched'] is False and r['M1_initializer_host_called'] is False
assert r['T4_data_unchanged'] and r['existing_MIDI_fields_unchanged']
m={x['label']:x for x in r['steps']}
for label,word in [('encoder_1',0xad32),('encoder_2',0xadb2),('encoder_3',0xadd0),('change_before_reload',0xa9d0),('load_confirm',0xadd0),('reload_apply',0xadd0)]:
    assert m[label]['MIDI_settings_word']==word,(label,m[label])
assert r['serialized_settings_after_save']==0xadd0
assert m['change_before_reload']['M1_config']==[0,3,80,0]
assert m['reload_apply']['M1_config']==[1,3,80,0]
assert m['reload_apply']['UI_data']==m['encoder_3']['UI_data']==m['reload_apply']['owner']
result={'PC_only':True,'passed':True,'candidate':'E08D','native_project_save_reload':True,
    'same_address_replacement_while_quiescent':True,'owner_rebound_after_reload':True,
    'T4_and_existing_MIDI_fields_unchanged':True,'serialized_saved_word':hex(r['serialized_settings_after_save']),
    'parameter_address':m['reload_apply']['UI_data'],
    'limits':['Stopped/quiescent project replacement; not project replacement while live held/queued notes remain.',
              'This directly tests E08D; E08E adds a Stop/OFF clear and requires its own playback regression.']}
Path('outputs/Digitone-E08D-project-readiness-results.json').write_text(json.dumps(result,indent=2));print(result)
