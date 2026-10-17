from pathlib import Path
import sys,struct,re,json,hashlib,importlib
root=Path(__file__).resolve().parents[1]
exec((root/'work/disassemble.py').read_text().split('out=[]')[0]);md.skipdata=True
anchors={0x400efc56:'203c4199d50c',0x400efc5c:'23c04199d520',0x400efc68:'23c04199d50c',0x400efc7a:'23c0431dc4c0',0x400efc86:'23c0431dc4b8',0x400efc8c:'41f9431dbfb8',0x400efca6:'b1fc431dc4b8',0x400eff72:'b5f9431dc4c0',0x400eff78:'670000b6',0x400eff7c:'202a0010',0x400eff86:'202a000c',0x400efede:'2688',0x400efee6:'2688',0x400efee8:'20b9431dc4c0',0x400f0012:'2089',0x400f001c:'2091',0x400f002a:'2480',0x4009bd08:'4eb9400f00ea',0x4009bd52:'23c0400002fc',0x400004ba:'207c40242000',0x400004c0:'223c431dc690',0x400256da:'4e90',0x400256ec:'4e94',0x400208bc:'4eb9400134e4',0x40008dfe:'b093',0x40008e00:'660000a2'}
for a,h in anchors.items():
 actual=b[a-base:a-base+len(bytes.fromhex(h))].hex()
 assert actual==h,(hex(a),actual,h)
payload_literal_refs={f'{t:08x}':[f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',t)),b)] for t in range(0x4199d510,0x4199d520,4)}
assert all(not refs for refs in payload_literal_refs.values())
sys.path.insert(0,str(root/'outputs'))
names=['digitone_behavior_model','digitone_event_context_model','digitone_firmware_route_checks','digitone_retained_pitch_checks','digitone_descriptor_provenance_checks','digitone_queue_snapshot_checks','digitone_writer_interleaving_checks','digitone_active_writer_checks','digitone_interrupt_capture_checks','digitone_transaction_handoff_checks','digitone_busy_capture_checks']
suites={name:importlib.import_module(name).checks() for name in names}
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
result=dict(specification_only=True,safe_storage_certified=False,candidate='First queue sentinel payload: depth 4199d510, state 4199d514',verified_byte_anchors={f'{a:08x}':h for a,h in anchors.items()},candidate_payload_literal_references=payload_literal_refs,suite_count=len(suites),total_scenarios=sum(r['scenarios_passed'] for r in suites.values()),suites=suites,unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)))
(root/'outputs/Digitone-busy-capture-check-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('All',len(suites),'suites pass:',result['total_scenarios'],'scenarios;',len(anchors),'byte anchors; sentinel literal search clear; hashes unchanged')
