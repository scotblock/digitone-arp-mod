from pathlib import Path
import json,statistics,hashlib
r=json.loads(Path('outputs/Digitone-E08-M1-tempo-playback.json').read_text());assert r['failure'] is None and r['halted'] is None and r['MIDI_received']==r['MIDI_delivered'] and r['native_code_preserved']
assert r['native_active_at_end']==r['native_busy_at_end']==r['native_count_at_end']==0
active={};ons=[];offs=[]
for event in r['wire']:
 assert len(event['bytes'])%3==0
 for i in range(0,len(event['bytes']),3):
  status,note,velocity=event['bytes'][i:i+3];assert status&240 in [128,144]
  key=(status&15,note)
  if status&240==144 and velocity>0:
   assert key not in active;active[key]=event['ms'];ons.append({'ms':event['ms'],'note':note})
  else:
   assert key in active;start=active.pop(key);offs.append({'ms':event['ms'],'note':note,'gate_ms':event['ms']-start})
assert not active and len(ons)==len(offs) and [x['note'] for x in ons]==([60,64,67]*((len(ons)+2)//3))[:len(ons)]
phases=[]
for p in r['phases']:
 on_times=[x['ms'] for x in ons if p['begin_ms']<=x['ms']<p['end_ms']];d=[b-a for a,b in zip(on_times,on_times[1:])]
 assert len(d)>=3
 phases.append({'phase':p['phase'],'interval_units':p['interval_units'],'gate_units':p['gate_units'],'musical_clock_units_per_second':p['clock_delta']*1000/(p['end_ms']-p['begin_ms']),'mean_step_ms':statistics.mean(d),'min_step_ms':min(d),'max_step_ms':max(d),'observed_note_ons':len(on_times)})
assert len(phases)==4 and phases[0]['musical_clock_units_per_second']>phases[2]['musical_clock_units_per_second']*1.02
for p in phases:
 expected=p['interval_units']*1000/p['musical_clock_units_per_second'];assert abs(p['mean_step_ms']-expected)<6,(p,expected);p['step_ms_predicted_from_native_clock']=expected
assert 1.9<phases[3]['mean_step_ms']/phases[2]['mean_step_ms']<2.1
assert phases[3]['gate_units']==phases[2]['gate_units'] and phases[3]['interval_units']==phases[2]['interval_units']*2
assert max(x['ms'] for x in offs)<r['release_request_ms']+70
r['passed']=True;r['verified_tempo_phases']=phases;r['note_on_count']=len(ons);r['matching_note_off_count']=len(offs);r['no_hanging_notes']=True
r['limits']=['Native UI LEVEL changes were delivered in bulk and did not produce preset target BPM values. Evidence is actual native clock-rate change and the matching measured arp step intervals, not assumed 60/120/180 settings.','Initial/native clock rate 43.2 million units/s slowed to about 41.4 million units/s. Step cadence has native MIDI-task polling jitter.','Native settings requests execute inside the MIDI consumer. Host publishes test requests; no user-facing settings page or persistence yet.','Playback uses relocated helpers loaded as a disclosed PC overlay and native initialization in a temporary frame. Cold copier/initialization is a separate isolated test, not one continuous boot-to-playback proof.','No packed E08 image, physical cache/RAM ownership proof or hardware trial.']
Path('outputs/Digitone-E08-M1-tempo-playback.json').write_text(json.dumps(r,indent=2))
layout=json.loads(Path('work/os144/E08-PC-install-layout.json').read_text());contracts=json.loads(Path('outputs/Digitone-E08-M1-relocated-tempo-contracts.json').read_text());copy=json.loads(Path('outputs/Digitone-E08-PC-copier-initialization.json').read_text());assert contracts['passed'] and copy['passed']
sha=hashlib.sha256(Path('outputs/Digitone_OS1.44E07_SCALE_DEGREE_ARP_DIN_MIDI_PC_ONLY.syx').read_bytes()).hexdigest();assert sha=='a8abfd22d9c65bd8dd65a6766e1fe5410ee343c50835946e900835242d7902bd'
summary={'PC_only':True,'passed':True,'E07_unchanged_sha256':sha,'hardware_ready':False,'installable_E08_produced':False,'native_settings':{'rates':layout['rate_labels'],'gate_percent_range':[1,99],'applied_by_native_MIDI_consumer':True,'settings_UI':False,'persistent_settings':False},'tempo_phases':phases,'note_on_count':len(ons),'matching_note_off_count':len(offs),'relocated_contract_groups':contracts['groups'],'copier_cases':len(copy['cases']),'loading_layout':{k:layout[k] for k in ['payload_bytes','additional_copy_bytes','copy_longwords','copy_source','copy_source_end','copy_destination_end','state','state_bytes','arena','arena_bytes','bootstrap','code_bytes']},'limits':r['limits'],'next':['Verify a packed loader-derived startup state through cache handoff, application initialization and M1 playback with no host code loading.','Connect mode/rate/gate requests to usable MIDI-track controls and decide per-pattern storage/persistence.','Audit the added RAM range and reinitialization/reset routes before any hardware candidate.']}
Path('outputs/Digitone-E08-tempo-and-loading-results.json').write_text(json.dumps(summary,indent=2))
text='''# E08 M1 — native tempo settings and loading layout

E07 remains unchanged. This phase produced native helpers and decompressed PC MAIN/payload images, not an installable E08 firmware.

## Tempo and settings

The retained native clock writer at 0x40095566 publishes the sequencer position, and its next position is advanced by 900,000 units. The relevant clock follows stock tempo in the observed UI controls. The arp scheduler continues to use that clock; no second millisecond clock was added.

Native configuration now supports 1/4, 1/8, 1/16, 1/32, 1/48, 1/96, 1/8 triplet and 1/16 triplet rates, with gate percentages 1–99. A guarded pending request is applied by the native MIDI consumer. Invalid requests preserve the previous configuration. A COLD admission guard prevents the M1 scheduler capturing or generating before LIVE. The public UI and persistence are not implemented.

The slowest table rate has 21,600,000 interval units. Native gate storage is half the desired duration because the stock timed-note retirement path doubles that field. Configuration arithmetic is bounded to avoid multiplication overflow. All 40 rate/gate combinations in the chosen controls passed native execution.

## Playback evidence

'''
for p in phases:text+=f"- {p['phase']}: mean step {p['mean_step_ms']:.2f} ms; native clock rate {p['musical_clock_units_per_second']:.0f} units/s.\n"
text+=f"\nThe clock slowed from about 43.2 to 41.4 million units/s, and the measured arp interval increased accordingly. At the slower tempo, changing 1/16 to 1/8 doubled the step interval. Changing gate 50% to 25% at the same time retained the same absolute gate units. All {len(ons)} notes had matching endings and the final scheduler, held set and descriptor arena were inactive. Bulk encoder input did not establish exact preset BPM targets; results use measured stock clock rates. Native polling jitter remains.\n"
text+=f'''
## Loading and initialization layout

The proposed copied payload grows from {layout['old_payload_bytes']:,} to {layout['payload_bytes']:,} bytes, an extension of {layout['additional_copy_bytes']:,} bytes. The copier's longword count becomes {layout['copy_longwords']:,}. Existing E07 helpers retain their addresses; added routines are packed after the old payload and their absolute references relocated. Data/state guard gaps are explicit.

- Copy source: 0x{layout['copy_source']:08x} through 0x{layout['copy_source_end']:08x} (exclusive end).
- Copy destination ends at 0x{layout['copy_destination_end']:08x}.
- M1 state: 0x{layout['state']:08x}, {layout['state_bytes']} bytes.
- Owned descriptor arena: 0x{layout['arena']:08x}, {layout['arena_bytes']} bytes.
- Cold-success initialization thunk: 0x{layout['bootstrap']:08x}.

The existing cold seed first checks its inherited caller/admission/context conditions. Only its successful continuation invokes the native M1 initializer. M1 defaults OFF, and its rate/gate defaults are created by the native configuration helper. The thunk then returns to the existing stock cache-handoff entry. A wrong caller reaches the inherited failure stop without calling the M1 initializer.

{contracts['groups']} relocated native contract groups passed, including request publication and COLD refusal. Isolated cold copier execution verified exact code/table copying, initialization defaults, a zeroed descriptor arena and no writes beyond the destination. The final playback run verified code preservation at the relocated addresses.

## Limits and next step

The copier test stops at the stock cache-handoff entry. Playback starts from a settled E07 snapshot with disclosed overlay loading. These are separate tests: full loader-to-copier-to-application-to-M1 continuity is not established. No packed container was produced during this phase. The added RAM range has no exclusive ownership or physical cache-coherence certification. Warm copier replay remains an inherited hazard; the extension does not make it safe.

Next: join actual startup and playback using a PC-only packed image, then connect usable MIDI-track controls and settle pattern persistence. Hardware trials require a separate readiness review.

## Evidence

'''
for name in ['Digitone-E08-tempo-and-loading-results.json','Digitone-E08-M1-tempo-playback.json','Digitone-E08-M1-relocated-tempo-contracts.json','Digitone-E08-PC-copier-initialization.json']:
 text+='- ['+name+']('+str(Path('outputs',name).resolve()).replace('\\','/')+')\n'
Path('outputs/Digitone-E08-tempo-and-loading.md').write_text(text,encoding='utf-8')
print('PASS:',len(ons),'pairs; tempo/rate controls;',contracts['groups'],'relocated groups;',layout['additional_copy_bytes'],'added copy bytes')
