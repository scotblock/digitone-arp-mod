exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
anchors={
 0x400f0224:'226f0010',0x400f0228:'246f0014',0x400f0232:'6f58',0x400f023c:'20394199d4f4',0x400f0244:'41f94199d224',0x400f024c:'06820000005a',0x400f0262:'5280',0x400f0274:'7459',0x400f0276:'b480',0x400f0278:'6c02',0x400f027a:'4280',0x400f027c:'5081',0x400f027e:'0c8100000100',0x400f0284:'66c4',0x400f0286:'23c04199d4f4',
 0x4009bcb8:'4878009e',0x4009bcbc:'4eb9400f0504',0x4009bcec:'4ebaffca',0x400f056a:'e78a',0x400f056c:'068200000014',0x400f057e:'2f03',0x400f0580:'4eb9400dab8c',0x400f058c:'23c04199d590',0x400f0592:'4eb9400ec284',0x400f059e:'20394199d590',0x400f05c0:'23c04199fe98',0x400f05c6:'9282',0x400f05ca:'42a80010',
 0x400eebac:'240f',0x400eebba:'200f',0x400eebc4:'4eb9400ec23c',0x400eec2a:'240f',0x400eec38:'200f',0x400eec42:'4eb9400ec23c',0x400eeca4:'240f',0x400eecb8:'200f',0x400eecc2:'4eb9400ec23c',
 0x400efbaa:'45f9400f0626',0x400efbc2:'4e92',0x400efbda:'4bf9400ec23c',0x400efbe0:'4e95',0x400efbea:'4e92',0x400efbf0:'2400',0x400efc06:'2f02',0x400efc08:'4e95',0x400efc16:'4e92',0x400efc18:'2800',0x400efc2a:'4eb9400ec23c',
 0x400f062c:'20794199fea0',0x400f0636:'43e80044',0x400f063a:'23d14199fea0',0x400f0658:'2008',0x400f06c4:'4eb9400ec23c',0x4009de38:'068041345f08',0x4009ce3a:'2f0d',0x4009cd70:'4bf9400f0626',0x4009cd78:'260d',
 0x40095f3a:'226a0008',0x40095f3e:'240f',0x40095f42:'2042',0x40095f44:'4e91',0x400eeb68:'203c4020034c',
}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
policy=struct.unpack_from('>IIII',b,0x4020034c-base)
assert policy==(0x400ee7f8,0x400ee96c,0x400eea88,0x400ee7c0)
# Closed instruction graph for the ring, from confirmed entry rather than
# provisional linear decoding. Its only application store to the index is
# the final normalized store. Calls and outside transfers are forbidden.
s,e=0x400f021c,0x400f0296;todo=[s];seen={};returns=[];index_stores=[]
conditions={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
while todo:
 a=todo.pop()
 if a in seen:continue
 assert s<=a<e
 i=next(md.disasm(b[a-base:a-base+16],a,count=1));m=i.mnemonic.split('.')[0];seen[a]=f'{i.mnemonic} {i.op_str}'
 assert m not in {'jsr','bsr','jmp','dc','rte','trap','illegal'}
 if '$4199d4f4' in i.op_str and m=='move' and i.op_str.endswith('$4199d4f4.l'):index_stores.append(a)
 if m=='rts':returns.append(a);continue
 if m in conditions|{'bra'}:
  t=int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16);todo.append(t)
  if m!='bra':todo.append(a+i.size)
 else:todo.append(a+i.size)
assert index_stores==[0x400f0286] and returns==[0x400f0294]
transitions=[]
for head in range(90):
 x=head
 for n in range(32):
  assert 0<=x<=89 and 0<=x+90<=179
  x+=1
  if x>89:x=0
 assert x==(head+32)%90 and 0<=x<=89
 transitions.append(dict(initial=head,after_active_call=x,after_inactive_call=head))
stride=8*0x9e+0x14;requested=64*stride
assert stride==0x504 and requested==0x14100
for slot in range(64):
 start=slot*stride
 assert start+0x14+8*0x9e<=requested
assert 63*stride==0x13bfc
marker=(0x4199d510,0x4199d518)
for slot in range(128):
 p=0x4199da94+slot*0x48
 assert p+0x48<=0x4199fe94 and not (p<marker[1] and p+0x48>marker[0])
for track in range(4):
 p=0x41345f08+track*0x48
 assert not (p<marker[1] and p+0x48>marker[0])
entry=json.loads(pathlib.Path('work/ring-entry-discovery.json').read_text())
external=[x for x in entry['encoded_transfers_into_routine'] if not x['source_inside_routine']]
assert not external
candidate=json.loads(pathlib.Path('work/marker-pointer-candidate-traces.json').read_text())
index_candidates=[{k:v for k,v in x.items() if k!='context'} for x in candidate['nearby_constant_stores'] if int(x['destination'],16)<0x4199d4f8 and int(x['destination'],16)+x['size']>0x4199d4f4]
assert [x['site'] for x in index_candidates]==['400f0286']
output_offsets=[frame*8+channel*4 for frame in range(32) for channel in range(2)]
assert max(output_offsets)+4==0x100
output_alias=0x4199d4f4
assert output_alias+output_offsets[7]==marker[0]
owners=[
 dict(sites=['400f0592'],owner='persistent heap allocation retained in 4199d590',requested_bytes=requested,record_stride=stride,record_count=64,status='Recovered initializer route resolved; valid allocation/configuration required; local allocation-failure handling not established'),
 dict(sites=['400efbe0','400efc08','400efc2a'],owner='event allocated by 400f0626 from fixed pool 4199da94..4199fe94',length=0x48,status='Destination routes resolved under event free-list invariants; null rejection visible'),
 dict(sites=['400f06c4'],caller='4009ce3c',owner='new event allocated through 400f0626',length=0x48,status='Pool destination; retained template is source'),
 dict(sites=['400f06c4'],caller='4009de40',owner='retained template 41345f08 + 0x48*track',length=0x48,status='Destination resolved for valid synth track 0..3'),
 dict(sites=['400eebc4','400eec42','400eecc2'],owner='temporary 0x18-byte current-stack argument area',length=0x18,status='Relative stack ownership resolved; absolute stack reservations not globally certified'),
 dict(sites=['400ee8b0','400ee992','400eeac6'],owner='caller descriptor buffer in a0/a2, selected via policy table 4020034c',length=0x18,status='Confirmed policy dispatch callers pass stack-relative descriptor buffers; arbitrary computed callers not certified'),
]
paths=[pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),pathlib.Path('work/section-3.bin')]
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r=dict(read_only=True,global_storage_certified=False,firmware_guard_implemented=False,ring_output_caller_status='No recovered external entry or stored function pointer; output argument unresolved',ring_entry_search=entry,ring_graph=dict(start=f'{s:08x}',end_exclusive=f'{e:08x}',instructions={f'{a:08x}':v for a,v in sorted(seen.items())},index_store=f'{index_stores[0]:08x}',normal_return=f'{returns[0]:08x}',calls=[]),ring_argument_ranges=dict(output_bytes=0x100,input_bytes=0x100,output_alias_dependency=dict(hypothetical_output_pointer=f'{output_alias:08x}',first_store_overwrites_index=True,output_offset=output_offsets[7],overlap_address=f'{marker[0]:08x}',runtime_caller_established=False)),index_status='Startup zero plus sole recovered direct writer preserve 0..89 only if output stores and other aliases do not overwrite index',index_transitions=transitions,index_store_candidates=index_candidates,policy_table=dict(address='4020034c',slots=[f'{x:08x}' for x in policy]),nearby_destination_owners=owners,verification=dict(byte_anchor_count=len(anchors),verified_byte_anchors={f'{a:08x}':h for a,h in anchors.items()},ring_initial_states=90,payload_records=64,event_destinations=128,retained_templates=4),limitations=['No proof that the ring routine is unreachable','No complete global index-alias or points-to proof','Ring output pointer must exclude index and marker; input pointer ownership unresolved','Valid allocator, free-list and synth-track invariants assumed for bounded ownership','Absolute stack locations and arbitrary computed policy callers not certified','Generic 400f09a4/400f0954 destinations still depend on callers'],unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)))
pathlib.Path('outputs/Digitone-ring-index-and-RAM-owner-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(byte_anchors=len(anchors),ring_instructions=len(seen),ring_entry_callers_found=len(external),index_store_candidates=len(index_candidates),payload_stride=hex(stride),payload_bytes=hex(requested),destination_owner_groups=len(owners),hashes_unchanged=True),indent=2))
