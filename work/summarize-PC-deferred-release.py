from pathlib import Path
import sys,json,hashlib,zlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
get=lambda n:json.loads(Path('outputs/Digitone-E04-PC-'+n+'.json').read_text())
controls=get('deferred-release-controls');panel=get('deferred-release-panel');startup=get('deferred-release-startup-startup');fault=get('deferred-release-failure');multi=get('deferred-release-multiplicity');publication=get('deferred-release-publication')
assert all(r['passed'] for r in [controls,startup,fault,multi,publication]) and all(c['passed'] for c in panel['cases'])
spec=json.loads(Path('work/os144/PC_ONLY-deferred-release-overlay.json').read_text());code=Path('work/os144/PC_ONLY-deferred-release-overlay.bin').read_bytes();assert hashlib.sha256(code).hexdigest()==spec['sha256']
old=json.loads(Path('work/os144/PC_ONLY-joined-UI-layout.json').read_text());hooks={h['site']:h for h in old['hooks']};hooks.update({h['site']:h for h in spec['hooks']})
for c in startup['cases']:
 saved=snapshot._load_blob(c['ui_snapshot'])
 def read(a,n):
  base=max(p for p in saved['pages'] if p<=a);d=zlib.decompress(saved['pages'][base]);v=d[a-base:a-base+n];assert len(v)==n;return v
 for h in hooks.values():
  if h['name']!='seed_after_copy':assert read(h['site'],h['length']).hex()==h['replacement']
 assert read(spec['base'],len(code))==code and int.from_bytes(read(0x47be2840,4),'big')==0x4c495645 and read(spec['count'],spec['storage_bytes'])==bytes(spec['storage_bytes'])
for c in panel['cases']:
 if c['mode'] in ['held_then_closed','two_held']:
  assert c['retained_count_before_resume'] in [1,2] and c['retained_count_after_resume']==0
  assert all(e['phase']=='0x494e4954' for e in c['native_drain_events'])
for p,h in get('input-live-summary')['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
r={'PC_only':True,'passed':True,'overlay_bytes':spec['bytes'],'fixture_queue_bytes':spec['storage_bytes'],'capacity':spec['capacity'],'boolean_refusal_controls':len(controls['boolean_controls']),'native_panel_sessions':len(panel['cases']),'native_cold_startup_cases':len(startup['cases']),'final_startup_snapshot_code_and_hooks_verified':True,'panel_one_and_two_note_cleanup_before_LIVE':True,'same_pitch_multiplicity_fixture_passed':True,'overflow_and_injected_failure_keep_admission_closed':True,'LIVE_store_occurs_after_drain_under_IPL7':True,'known_boolean_refusal_returns_explicit_handled':True,'all_computed_callers_certified':False,'physical_queue_RAM_ownership_and_native_initialization_certified':False,'naturally_scheduled_warm_close_resume_proven':False,'actual_exception_recovery_certified':False,'firmware_unchanged':True,'hardware_ready':False}
Path('outputs/Digitone-E04-PC-deferred-release-summary.json').write_text(json.dumps(r,indent=2));print('PASS final deferred release, startup, publication and unchanged firmware')
