from pathlib import Path
import sys,json,hashlib,zlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
get=lambda n:json.loads(Path('outputs/Digitone-E04-PC-'+n+'.json').read_text())
start=get('joined-UI-startup-startup');routes=get('joined-UI-routes');life=get('joined-UI-lifecycle');panel=get('joined-UI-panel-tests');layout=json.loads(Path('work/os144/PC_ONLY-joined-UI-layout.json').read_text())
assert all(r['passed'] for r in [start,routes,life]) and all(c['passed'] for c in panel['cases'])
for c in start['cases']:
 blob=snapshot._load_blob(c['ui_snapshot'])
 def read(a,n):
  base=max(p for p in blob['pages'] if p<=a);data=zlib.decompress(blob['pages'][base]);answer=data[a-base:a-base+n];assert len(answer)==n;return answer
 for h in [h for h in layout['hooks'] if h['name']!='seed_after_copy']:assert read(h['site'],h['length']).hex()==h['replacement']
 assert int.from_bytes(read(0x47be2840,4),'big')==0x4c495645
cases={c['mode']:c for c in panel['cases']}
for c in panel['cases']:
 assert not c['forced_semaphore_unblock']
 assert all(m['panel']['consumed']==m['panel']['produced'] for m in c['marks'])
a,b=cases['LIVE']['marks'][-2:];assert 'live_producer' in a['events'] and 'publish' in a['events'] and 'pitch' in a['events'] and 'internal_release' in b['events'] and 'sustain_release' in b['events'] and 'publish' in b['events']
assert a['note_counts'][1]==1 and b['note_counts'][1]==0
for mode in ['INITIALIZING','held_then_closed']:
 c=cases[mode];press,release=c['marks'][-2:];assert 'publish' not in release['events'] and 'sustain_release' in release['events']
 assert all(int(e['D0'],16)&255 for e in c['events'] if e['kind']=='release_decision' and e['phase']=='0x494e4954')
assert cases['INITIALIZING']['marks'][-2]['note_counts']==[0]*8
assert cases['held_then_closed']['marks'][-1]['note_counts'][1]==1
hashes=get('input-live-summary')['hashes']
for p,want in hashes.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==want
for name in ['input-live','release-reset']:
 cfg=json.loads(Path('work/os144/PC_ONLY-'+name+'-overlay.json').read_text());assert hashlib.sha256(Path('work/os144/PC_ONLY-'+name+'-overlay.bin').read_bytes()).hexdigest()==cfg['sha256']
r={'PC_only':True,'passed':True,'joined_hooks':len(layout['hooks']),'final_native_startup_cases':len(start['cases']),'explicit_and_retained_UI_route_cases':len(routes['cases']),'UI_lifecycle_runs':len(life['cases']),'close_reentry_cycles':sum(c['cycles'] for c in life['cases']),'panel_sessions':len(panel['cases']),'panel_receiver_consumes_all_bytes':True,'LIVE_panel_press_publish_pitch_release_confirmed':True,'closed_panel_new_note_blocked':True,'tested_panel_release_aborts_via_nonzero_preserved_D0':True,'closed_held_panel_note_remains_retained':True,'automatic_closed_release_replay_implemented':False,'panel_return_contract_universal':False,'unknown_computed_UI_routes_certified':False,'hardware_ready':False,'firmware_unchanged':True}
Path('outputs/Digitone-E04-PC-joined-UI-summary.json').write_text(json.dumps(r,indent=2));print('PASS joined startup/UI lifecycle and actual panel routes')

