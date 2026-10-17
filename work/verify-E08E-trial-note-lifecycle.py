from pathlib import Path
import json
r=json.loads(Path('outputs/Digitone-E08E-trial-note-lifecycle.json').read_text())
assert r['passed'] and r['halted'] is None and not r['failure']
assert r['MIDI_received']==r['MIDI_delivered']
assert all(r[k] is False for k in ['helpers_host_loaded','hooks_host_patched','M1_initializer_host_called','settings_host_written'])
source=Path('work/verify-E08C-packaged-controls.py').read_text();a=source.index('def packets(events):');z=source.index('\nactive, ons, offs',a)
exec(compile(source[a:z],'independent-MIDI-parser','exec'))
active={};ons=[];offs=[]
for e in packets(r['wire']):
    key=(e['status']&15,e['note'])
    if e['status']&0xf0==0x90 and e['velocity']:
        assert key not in active,(key,e)
        active[key]=e;ons.append(e)
    else:
        assert key in active,(key,e)
        active.pop(key);offs.append(e)
assert not active and len(ons)==len(offs)
m={x['label']:x for x in r['marks']}
assert m['after_held_Stop']['state']==[1,0,0,0,0]
assert not [e for e in ons if e['phase']=='held_Stop' and e['ms']>r['held_Stop_ms']+80]
assert m['sustain_keys_up']['state'][1:4]==[1,1,3]
assert m['sustain_pedal_up']['state'][1]==0 and m['sustain_pedal_up']['state'][3:]==[0,0]
for label in ['mode_OFF_held','release_while_OFF','re_enable_idle']:
    assert m[label]['state'][1:]==[0,0,0,0]
assert not [e for e in ons if e['phase']=='re_enable_idle']
assert m['fresh_after_re_enable']['state'][1:4]==[1,1,3]
assert m['final_stop']['state']==[1,0,0,0,0]
result={'PC_only':True,'passed':True,'candidate_sha256':r['candidate_sha256'],
 'native_held_Stop_stops_generation':True,'no_late_restart_after_Stop':True,
 'native_CC64_holds_then_pedal_release_clears':True,'OFF_clears_membership':True,
 'UP_does_not_recall_released_notes':True,'fresh_notes_after_UP_work':True,
 'note_ons':len(ons),'matched_note_offs':len(offs),'hanging_notes':0,
 'limits':['Single M1 live-input workload; external CC120/123, MIDI clock transport, congestion and simultaneous synth/MIDI arps are not covered by this test.']}
Path('outputs/Digitone-E08E-trial-note-lifecycle-results.json').write_text(json.dumps(result,indent=2));print(result)
