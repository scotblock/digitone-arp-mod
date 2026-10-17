from pathlib import Path
import json,hashlib
p=Path('outputs/Digitone-E04-PC-resident-successor-writer-summary.json');r=json.loads(p.read_text())
assert r['passed'] and r['confirmed_pattern_replacement'] and r['software_transfer_refusals']==0 and not r['software_errors']
assert all(not v['overlaps'] and not v['unknowns'] for v in r['payload_destination_groups'].values())
assert all(v['aligned'] and not v['descriptor_overlap'] and int(v['pointer'],16)!=0 for v in r['successor_nodes'])
for edge in r['minor_link_targets']:
 kind,parts=edge.split(':');a,b=parts.split('->');assert kind=='minor' and a==b
assert not r['bulk_overlap'] and not r['guest_queue_writers'] and not r['host_queue_writes']
old=json.loads(Path('outputs/Digitone-E04-PC-input-live-summary.json').read_text())
for file,h in old['hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
spec=json.loads(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.json').read_text());assert hashlib.sha256(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.bin').read_bytes()).hexdigest()==spec['sha256']
r['observed_successor_resolution_passed']=True;r['self_link_destination_identity_resolved_for_observed_configs']=True;r['physical_self_link_and_future_reprogramming_certified']=False;r['exclusive_storage_ownership_certified']=False;r['firmware_and_overlay_unchanged']=True;p.write_text(json.dumps(r,indent=2));print('PASS',len(r['successor_nodes']),'concrete successor locations;',r['actual_software_links_followed'],'traversals; no queue overlap')
