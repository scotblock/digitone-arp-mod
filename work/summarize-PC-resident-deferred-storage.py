from pathlib import Path
import json,hashlib,zlib,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import snapshot
get=lambda n:json.loads(Path('outputs/Digitone-E04-PC-'+n+'.json').read_text())
screen=get('deferred-storage-screen');start=get('resident-deferred-startup-startup');controls=get('resident-deferred-controls');panel=get('resident-deferred-panel');life=get('resident-deferred-lifetime')
spec=json.loads(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.json').read_text());code=Path('work/os144/PC_ONLY-resident-deferred-release-overlay.bin').read_bytes();assert hashlib.sha256(code).hexdigest()==spec['sha256']
assert controls['passed'] and start['passed'] and life['passed'] and all(c['passed'] for c in panel['cases'])
assert not start['deferred_queue_zero_initialized_by_host_fixture'] and not start['additional_storage_host_cleared']
for c in start['cases']:
 assert c['deferred_initialization_checks']==[{'pc':'0x4029c518','queue_all_zero':True,'phase_before_seed':0}]
 assert c['deferred_storage_writes']['0x4029c4c2']['writes']==100
 for pc in c['deferred_storage_writes']:assert int(pc,16)==0x4029c4c2 or spec['base']<=int(pc,16)<spec['base']+spec['bytes']
 saved=snapshot._load_blob(c['ui_snapshot'])
 def read(a,n):
  base=max(p for p in saved['pages'] if p<=a);v=zlib.decompress(saved['pages'][base])[a-base:a-base+n];assert len(v)==n;return v
 assert read(spec['base'],len(code))==code and read(spec['count'],spec['storage_bytes'])==bytes(spec['storage_bytes'])
 for h in spec['hooks']:assert read(h['site'],h['length']).hex()==h['replacement']
for c in panel['cases']:
 assert c['adjacent_canaries_preserved']
 for pc in c['queue_writers']:assert spec['base']<=int(pc,16)<spec['base']+spec['bytes']
for p,h in get('input-live-summary')['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
prior=json.loads(Path('work/os144/PC_ONLY-deferred-release-overlay.json').read_text());assert hashlib.sha256(Path('work/os144/PC_ONLY-deferred-release-overlay.bin').read_bytes()).hexdigest()==prior['sha256']
r={'PC_only':True,'passed':True,'queue_start':hex(spec['count']),'queue_end':hex(spec['count']+spec['storage_bytes']),'bytes':spec['storage_bytes'],'source_start':screen['source'],'native_initialization_before_COLD_tested':True,'native_dirty_to_zero_startup_cases':len(start['cases']),'panel_sessions_using_native_initialized_storage':len(panel['cases']),'all_executed_guest_writers_accounted_for_in_tested_runs':True,'static_literal_candidates_in_stock_or_previous_payload':sum(len(x['aligned_word_candidates']) for x in screen['literal_screen']),'known_custom_layout_overlap':False,'global_computed_writes_and_bulk_DMA_excluded':False,'physical_exclusive_RAM_ownership_certified':False,'cold_only_recopy_provenance_certified':False,'new_host_zero_clear_required':False,'firmware_and_prior_artifacts_unchanged':True,'hardware_ready':False}
Path('outputs/Digitone-E04-PC-resident-deferred-storage-summary.json').write_text(json.dumps(r,indent=2));print('PASS resident queue: native initialization, observed owners and unchanged firmware')
