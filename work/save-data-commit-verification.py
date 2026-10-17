from pathlib import Path
import sys, json, hashlib, importlib
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'outputs'))
names=['digitone_behavior_model','digitone_event_context_model','digitone_firmware_route_checks','digitone_retained_pitch_checks','digitone_descriptor_provenance_checks','digitone_queue_snapshot_checks','digitone_writer_interleaving_checks','digitone_active_writer_checks','digitone_interrupt_capture_checks','digitone_transaction_handoff_checks','digitone_busy_capture_checks','digitone_writer_exit_checks','digitone_data_commit_checks']
suites={n:importlib.import_module(n).checks() for n in names}
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r=json.loads((root/'outputs/Digitone-data-only-closure-results.json').read_text())
r.update(suite_count=len(suites),total_scenarios=sum(x['scenarios_passed'] for x in suites.values()),suites=suites,unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)))
# Extend literal inventory to every raw address from which a signed 16-bit
# displacement could reach any marker byte. These are search candidates, not
# decoded references or alias proofs.
wide=[]
for section in [2,3]:
    data=(root/f'work/section-{section}.bin').read_bytes()
    counts={}
    for p in range(len(data)-3):
        v=int.from_bytes(data[p:p+4],'big')
        if 0x41995511<=v<=0x419a5517:
            key=f'{v:08x}'
            counts[key]=counts.get(key,0)+1
    wide.append(dict(section=section,raw_candidate_count=sum(counts.values()),distinct_bases=len(counts),base_counts=counts,limitation='Heuristic raw-byte search only; code/data alignment, provenance, indexed addressing and pointer loads are not certified'))
r['wider_signed_displacement_candidate_inventory']=wide
(root/'outputs/Digitone-data-only-closure-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(suites=len(suites),scenarios=r['total_scenarios'],firmware_hashes_unchanged=True,wide_candidates=[dict(section=x['section'],count=x['raw_candidate_count'],distinct=x['distinct_bases']) for x in wide]),indent=2))
