from pathlib import Path
import json, hashlib, statistics, struct

out = Path('outputs')
read = lambda name: json.loads((out/name).read_text())
r = read('Digitone-E08C-packaged-panel-playback.json')
assert r['passed'] and not r['failure'] and r['halted'] is None
assert r['MIDI_received'] == r['MIDI_delivered']
assert r['final_state'] == [0,0,0] and r['code_and_tables_preserved']
for field in ['helpers_host_loaded','hooks_host_patched','M1_initializer_host_called','settings_host_written']:
    assert r[field] is False, field

def packets(events):
    status = None
    pending = []
    result = []
    for event in events:
        for byte in event['bytes']:
            if byte >= 0xf8: continue
            if byte & 0x80:
                assert byte < 0xf0, ('unexpected system message', byte)
                status, pending = byte, []
                continue
            assert status is not None
            pending.append(byte)
            length = 1 if status&0xf0 in [0xc0,0xd0] else 2
            if len(pending) == length:
                if status&0xf0 in [0x80,0x90]:
                    result.append({'phase':event.get('phase'),'ms':event['ms'],
                                   'status':status,'note':pending[0], 'velocity':pending[1]})
                pending = []
    assert not pending
    return result

active, ons, offs = {}, [], []
for event in packets(r['wire']):
    key = event['status']&15, event['note']
    if event['status']&0xf0 == 0x90 and event['velocity']:
        assert key not in active, ('duplicate sounding note', event)
        active[key] = event
        ons.append(event)
    else:
        assert key in active, ('unmatched note off', event)
        start = active.pop(key)
        offs.append({**event, 'gate_ms':event['ms']-start['ms']})
assert not active and len(ons)==len(offs)
off_ons = [e for e in ons if e['phase']=='OFF_chord']
assert [e['note'] for e in off_ons]==[60,64,67]
assert max(e['ms'] for e in off_ons)-min(e['ms'] for e in off_ons)<5
for phases in [{'UP_start','UP_1_32_gate80','tempo_plus400_1_32','tempo_minus800_1_32'},
               {'UP_second','UP_1_16_gate50'}]:
    notes=[e['note'] for e in ons if e['phase'] in phases]
    assert len(notes)>=6 and notes==([60,64,67]*((len(notes)+2)//3))[:len(notes)], notes

cadence=[]
for sample in r['samples']:
    times=[e['ms'] for e in ons if sample['begin_ms']<=e['ms']<sample['end_ms']]
    deltas=[b-a for a,b in zip(times,times[1:])]
    assert len(deltas)>=4
    rate=sample['clock_delta']*1000/(sample['end_ms']-sample['begin_ms'])
    predicted=sample['interval_units']*1000/rate
    observed=statistics.mean(deltas)
    assert abs(predicted-observed)<8,(sample['phase'],predicted,observed)
    gates=[e['gate_ms'] for e in offs if sample['begin_ms']<=e['ms']<sample['end_ms']]
    gate_prediction=sample['gate_units']*2000/rate
    assert gates and abs(statistics.mean(gates)-gate_prediction)<8,(sample['phase'],gates,gate_prediction)
    cadence.append({'phase':sample['phase'],'clock_units_per_second':rate,
                    'predicted_step_ms':predicted,'mean_step_ms':observed,
                    'predicted_gate_ms':gate_prediction,'mean_gate_ms':statistics.mean(gates),
                    'note_ons':len(times)})
assert len(cadence)==4
assert cadence[0]['clock_units_per_second'] > cadence[2]['clock_units_per_second']*1.01
assert 1.8 < cadence[3]['mean_step_ms']/cadence[2]['mean_step_ms'] < 2.2
assert max(e['ms'] for e in offs)<r['last_release_ms']+150

# A MIDI artifact contains the actually observed output for independent listening
# or inspection, without requiring usable real-time Digiemu audio.
def vl(value):
    result=[value&127];value>>=7
    while value:result.insert(0,(value&127)|128);value>>=7
    return bytes(result)
track=bytearray(b'\0\xff\x51\x03\x07\xa1\x20')
base=packets(r['wire'])[0]['ms'];last=0
for event in packets(r['wire']):
    tick=round((event['ms']-base)*.96)
    track+=vl(tick-last)+bytes([event['status'],event['note'],event['velocity']]);last=tick
track+=b'\0\xff\x2f\0'
mid=out/'Digitone-E08C-packaged-M1-observed-PC.mid'
mid.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)
playback={'PC_only':True,'passed':True,'note_on_count':len(ons),
          'matching_note_off_count':len(offs),'no_hanging_notes':True,
          'OFF_chord_passes_through':True,'UP_ascending_chord':True,
          'settings_from_panel':True,'cadence':cadence,'MIDI_file':str(mid.resolve()),
          'helpers_host_loaded':False,'settings_host_written':False,
          'input_gate_fixture':r['input_gate_fixture']}
(out/'Digitone-E08C-packaged-playback-verification.json').write_text(json.dumps(playback,indent=2))
print(json.dumps(playback,indent=2))

if '--playback-only' not in __import__('sys').argv:
    loader=read('Digitone-E08C-packed-loader.json')
    startup=read('Digitone-E08C-PC-startup-comparison.json')
    copier=read('Digitone-E08C-PC-copier-initialization.json')
    layout=read('Digitone-E08C-PC-path-layout.json')
    control=read('Digitone-E08C-packaged-project-controls.json')
    assert loader['passed'] and startup['passed'] and copier['passed']
    assert loader['main_matches'] and loader['reached']=='0x400004e8' and not loader['flash_writes']
    assert all(c['passed'] and c['copied_components_verified'] and not c['strict_failures'] and not c['packaged_helpers_host_loaded'] for c in startup['cases'])
    assert not control.get('failure') and control.get('halted') is None
    assert control['helpers_host_loaded'] is False and control['hooks_host_patched'] is False and control['M1_initializer_host_called'] is False
    steps={e['label']:e for e in control['steps']}
    assert steps['M1_page']['M1_config']==[0,2,50,0]
    for name,word in [('encoder_1',0xad32),('encoder_2',0xadb2),('encoder_3',0xadd0),
                      ('change_before_reload',0xa9d0),('load_confirm',0xadd0),('reload_apply',0xadd0)]:
        assert steps[name]['MIDI_settings_word']==word,(name,steps[name])
    assert steps['reload_apply']['M1_config']==[1,3,80,0]
    assert control['T4_data_unchanged'] and control['existing_MIDI_fields_unchanged']
    assert control['serialized_settings_after_save']==0xadd0
    assert all(c['settings_tail_zeroed'] for c in copier['cases'])
    assert copier['cases'][0]['poisoned_before_native_init'] is True
    edit_phases={'M1_page','close','apply'}|{f'encoder_{i}' for i in range(1,9)}
    assert not [e for e in control['sound_lookups'] if e['phase'] in edit_phases]
    e07=out/'Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx'
    digest=hashlib.sha256(e07.read_bytes()).hexdigest()
    assert digest=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
    assert hashlib.sha256(Path(layout['candidate']).read_bytes()).hexdigest()==loader['candidate_sha256']==layout['candidate_sha256']==r['candidate_sha256']
    summary={'PC_only':True,'passed':True,'hardware_ready':False,'installable_release_produced':False,
             'candidate_sha256':layout['candidate_sha256'],'copied_payload_bytes':layout['payload_bytes'],
             'controls_added_copy_bytes':layout['controls_extension_bytes'],
             'loader_instructions':loader['instructions'],'packaged_startup_to_UI':True,
             'native_panel_project_save_reload':True,'T4_and_existing_MIDI_fields_unchanged':True,
             'helpers_host_loaded':False,'hooks_host_patched':False,
             'settings_host_written':False,'E07_unchanged_sha256':digest,
             'playback':playback,
             'limits':['Serialized modeled-state handoffs join loader, startup and playback; peripherals and ColdFire compatibility remain modeled.',
                       'The emulator MIDI input gate is a disclosed host fixture. Mode, rate and gate settings come from panel input.',
                       'Stop was checked after note release; this does not establish every held-note or sustain Stop case.',
                       'M1 only; actual pattern handoff isolation, reset/copy/destruction lifetimes and M2-M4 remain incomplete.',
                       'Physical RAM ownership, cache coherence and real-time audio timing remain unverified.']}
    (out/'Digitone-E08C-packaged-controls-results.json').write_text(json.dumps(summary,indent=2))
    print('PASS packaged loader, startup, panel/playback and native project save/reload.')
