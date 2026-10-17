from pathlib import Path
import sys, json, hashlib, importlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'outputs'))
names=['digitone_behavior_model','digitone_event_context_model','digitone_firmware_route_checks','digitone_retained_pitch_checks','digitone_descriptor_provenance_checks','digitone_queue_snapshot_checks','digitone_writer_interleaving_checks','digitone_active_writer_checks','digitone_interrupt_capture_checks','digitone_transaction_handoff_checks']
suites={name:importlib.import_module(name).checks() for name in names}
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
b=paths[1].read_bytes()
anchors={
0x40008ac8:'114003cb',0x40008b18:'114003ce',
0x40008dfc:'700a',0x40008dfe:'b093',0x40008e62:'0682000003d0',
0x40008fda:'2481',0x4000aecc:'b093',0x4000aeea:'0683000003cf',
0x4000aef0:'0682000003ce',0x4000af2e:'2480',0x4000b078:'b093',
0x4000b1e4:'b093',0x4000b202:'0683000003d0',0x4000b246:'2480',
0x4001330c:'206f0004',0x40013348:'114003cb',0x40013358:'114003ce',
0x40013514:'47fafdf6',0x40013524:'4e93',0x400208bc:'4eb9400134e4',
0x400225c2:'2f3c0001611d',0x400225cc:'4eb9400ec23c',
0x40024384:'4eb940008de0',0x400256dc:'2f3c0001611d',
0x400256ec:'4e94',0x400ec252:'4cd0003c',0x400ec258:'48d1003c',
0x40173e3c:'40134ff0',0x400efe94:'21400004',0x400efeac:'2140000c',
0x400efede:'2688',0x400effca:'116a00070018',0x400efff8:'2f08',
0x400efffa:'4e94',0x400f0024:'23ca431dc4c4',0x400f0656:'4290'}
for a,h in anchors.items():
 actual=b[a-0x40000400:a-0x40000400+len(bytes.fromhex(h))].hex()
 assert actual==h,(hex(a),actual,h)
# Confirm the resolved pattern backing getter independently of the table pointer.
assert b[0x40134ff0-0x40000400:0x40134ffa-0x40000400].hex()=='206f0004202800104e75'
anchors[0x40134ff0]='206f0004202800104e75'
result=dict(specification_only=True,suite_count=len(suites),total_scenarios=sum(r['scenarios_passed'] for r in suites.values()),suites=suites,verified_byte_anchors={f'{a:08x}':h for a,h in anchors.items()},unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)))
(root/'outputs/Digitone-six-pass-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['suites','verified_byte_anchors']},indent=2))
print('verified anchors',len(anchors))
for name,r in suites.items():print(name,r['scenarios_passed'])
