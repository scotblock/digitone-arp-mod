from pathlib import Path
import json,hashlib
get=lambda n:json.loads(Path('outputs/Digitone-E04-PC-'+n+'.json').read_text())
run=get('resident-storage-extended-runtime');calls=get('resident-copier-callers');static=get('resident-computed-write-screen')
assert run['passed'] and run['pattern_replacement_confirmed'] and run['queue_unchanged'] and not run['guest_writers'] and not run['host_queue_writes'] and not run['bulk_overlaps'] and not run['copier_or_reset_entries']
assert all(v['overlap_count']==0 for v in run['DMA_channels'].values())
assert calls['direct_call_candidates']==[{'pc':'0x40000538','kind':'JSR'}]
for p,h in get('input-live-summary')['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
spec=json.loads(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.json').read_text());assert hashlib.sha256(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.bin').read_bytes()).hexdigest()==spec['sha256']
r={'PC_only':True,'audit_checks_passed':True,'runtime_ms':run['elapsed_model_ms'],'confirmed_pattern_replacement':True,'monitored_memcpy_calls':run['bulk_calls']['memcpy'],'monitored_memset_calls':run['bulk_calls']['memset'],'bulk_destinations_overlapping_queue':0,'guest_or_host_API_queue_writes':0,'copier_replay_observed':False,'direct_copier_call_sites_found':1,'DMA_descriptor_observations':run['DMA_observation_count'],'DMA_channels_screened':len(run['DMA_channels']),'observed_DMA_destination_overlap':False,'DMA_scatter_successors_certified':False,'physical_DMA_safety_certified':False,'rooted_static_instruction_count':static['reached_instruction_count'],'computed_destination_candidates_unresolved':len(static['computed_destination_candidates']),'indirect_edges_unresolved':len(static['indirect_control_edges']),'unknown_static_boundaries':len(static['unknown_boundaries']),'exclusive_ownership_certified':False,'cold_only_recopy_provenance_certified':False,'hardware_ready':False,'firmware_and_resident_overlay_unchanged':True}
Path('outputs/Digitone-E04-PC-resident-storage-extended-summary.json').write_text(json.dumps(r,indent=2));print('PASS extended write/DMA/copy audit; exclusive ownership remains unproven')
