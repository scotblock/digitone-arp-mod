from pathlib import Path
import sys,json,hashlib,struct,re,importlib
root=Path(__file__).resolve().parents[1]
exec((root/'work/disassemble.py').read_text().split('out=[]')[0]);md.skipdata=True
anchors={0x40034c76:'4e75',0x40034d9a:'4e75',0x400353f6:'4e75',0x4001336e:'4e75',0x40013556:'6000ff20',0x40013562:'4e75',0x400134e2:'4e75',0x400208d8:'4e75',0x40008eae:'4e75',0x40008b6e:'4e75',0x400225ea:'4ed1',0x40025794:'4e75',0x400efc68:'23c04199d50c',0x400efc7a:'23c0431dc4c0',0x400eff72:'b5f9431dc4c0',0x400eff78:'670000b6',0x400efede:'2688',0x400efee6:'2688',0x400f001c:'2091',0x400ec280:'4e75',0x400ec2cc:'4e75',0x4013a33a:'206f0004202800104e75'}
for a,h in anchors.items():
 actual=b[a-base:a-base+len(bytes.fromhex(h))].hex()
 assert actual==h,(hex(a),actual,h)
queue_refs={}
for t in [0x4199d50c,0x4199d520,0x431dc4b8,0x431dc4bc,0x431dc4c0,0x431dc4c4]:
 queue_refs[f'{t:08x}']=[f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',t)),b)]
leaf_ranges={'memcpy':(0x400ec23c,0x400ec282),'memset':(0x400ec284,0x400ec2ce),'track_defaults':(0x4001330c,0x40013370),'track_import':(0x400089fa,0x40008b70)}
leaf_results={}
for name,(s,e) in leaf_ranges.items():
 items=list(md.disasm(b[s-base:e-base],s))
 calls=[hex(i.address) for i in items if i.mnemonic.split('.')[0] in ['jsr','bsr']]
 assert not calls
 leaf_results[name]=dict(start=f'{s:08x}',end_exclusive=f'{e:08x}',call_instructions=calls,limitation='No called application exception code; memory/CPU faults and interrupt effects not certified')
sys.path.insert(0,str(root/'outputs'))
names=['digitone_behavior_model','digitone_event_context_model','digitone_firmware_route_checks','digitone_retained_pitch_checks','digitone_descriptor_provenance_checks','digitone_queue_snapshot_checks','digitone_writer_interleaving_checks','digitone_active_writer_checks','digitone_interrupt_capture_checks','digitone_transaction_handoff_checks','digitone_busy_capture_checks','digitone_writer_exit_checks']
suites={name:importlib.import_module(name).checks() for name in names}
paths=[Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),root/'work/section-3.bin']
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
graphs=json.loads((root/'outputs/Digitone-writer-exit-graphs.json').read_text())
result=dict(specification_only=True,firmware_guard_implemented=False,global_storage_certified=False,exception_cleanup_certified=False,recovered_queue_lifetime_audited=True,writer_routines=len(graphs),reachable_instructions=sum(g['reachable_instruction_count'] for g in graphs),verified_byte_anchors={f'{a:08x}':h for a,h in anchors.items()},queue_pointer_literal_inventory=queue_refs,call_free_leaf_checks=leaf_results,suite_count=len(suites),total_scenarios=sum(r['scenarios_passed'] for r in suites.values()),suites=suites,unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)))
(root/'outputs/Digitone-storage-lifetime-and-writer-exit-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Verified',len(anchors),'anchors;',len(graphs),'writer graphs,',result['reachable_instructions'],'reachable instructions;',result['total_scenarios'],'scenarios in',len(suites),'suites; firmware unchanged')
