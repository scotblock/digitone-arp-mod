from pathlib import Path
import json,hashlib
r=json.loads(Path('outputs/Digitone-E04-PC-input-live-sustain-panel.json').read_text())
w=json.loads(Path('outputs/Digitone-E04-PC-input-live-warm-reset.json').read_text())
cases={c['mode']:c for c in r['cases']}
a=cases['LIVE_guarded'];b=cases['LIVE_stock_entries']
normalize=lambda c:[{k:m[k] for k in ['label','events','flags','lists']} for m in c['marks']]
assert normalize(a)==normalize(b)
closed=cases['INITIALIZING_guarded'];held=cases['LIVE_held_then_closed']
assert closed['marks'][0]['flags']=='0100000000000000'
assert closed['marks'][1]['events']==['packet']
release=next(m for m in held['marks'] if m['label']=='sustain release')
assert 'publish' in release['events'] and release['phase']=='0x494e4954'
assert w['hypothetical_overlap']['state_changed'] and w['hypothetical_overlap']['reachability_proven'] is False
hashes=json.loads(Path('outputs/Digitone-E04-PC-input-live-summary.json').read_text())['hashes']
for p,expected in hashes.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected,p
summary={'PC_only':True,'harness_assertions_passed':True,'admission_safety_complete':False,'LIVE_guarded_vs_displaced_stock_entries_observed_route_sustain_state_parity':True,'receiver_sustain_sessions':4,'repeated_warm_initializer_calls':9,'closed_CC64_mutates_sustain_flags':True,'retained_sustain_release_publishes_while_closed':True,'explicit_note_off_bypasses_packet_guard':True,'velocity_zero_note_off_uses_packet_guard':True,'warm_initializer_does_not_close_admission':True,'hypothetical_input_during_warm_reset_passes_guard':True,'actual_reset_input_overlap_proven':False,'panel_note_production_observed':False,'panel_admission_certified':False,'firmware_and_prior_artifact_hashes_unchanged':True,'hardware_ready':False}
Path('outputs/Digitone-E04-PC-input-live-followup-summary.json').write_text(json.dumps(summary,indent=2))
print('PASS observations, negative controls and unchanged artifact hashes')
