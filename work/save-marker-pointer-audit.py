"""Verify concrete byte anchors and bounded address sets, without RAM/device writes."""
exec(open('work/disassemble.py').read().split('out=[]')[0])
import json,hashlib
from collections import Counter
marker=(0x4199d510,0x4199d518)
def overlaps(start,size):return start<marker[1] and start+size>marker[0]
anchors={
 0x400004ba:'207c40242000',0x400004c0:'223c431dc690',0x400004d2:'48d000f0',0x400004d6:'41e80010',0x40000542:'4ebaff6e',
 0x400ef0a6:'41f94199cf41',0x400ef0ac:'43f94199cf61',0x400ef0d0:'41e80040',0x400ef0ee:'b1fc4199d041',
 0x400ef43a:'41f94199d024',0x400ef446:'2f480044',0x400ef4c0:'220a',0x400ef4c2:'068100000020',0x400ef512:'2f01',0x400ef514:'4eb9400ec23c',
 0x400ef7b0:'53af0038',0x400ef7b4:'45eaffe0',0x400ef7cc:'5285',0x400ef7ce:'d3af0044',0x400ef7d2:'7408',0x400ef7dc:'b485',
 0x400ef7ec:'48780200',0x400ef7f2:'48794199d024',0x400ef7f8:'48794199cd24',0x400ef7fe:'4eb9400ec23c',
 0x400f023c:'20394199d4f4',0x400f0244:'41f94199d224',0x400f024c:'06820000005a',0x400f025e:'21930c00',0x400f0270:'21932c00',0x400f0274:'7459',0x400f027a:'4280',0x400f027e:'0c8100000100',0x400f0286:'23c04199d4f4',
 0x4009d8d6:'48798000f270',0x4009d8de:'4eb9400f00ee',0x4009da6c:'48798000f270',0x4009da72:'4eb9400f00ee',
 0x400f018e:'25879800',0x400f0192:'7e30',0x400f01ea:'42b29800',0x400f01ee:'7830',
 0x400986c4:'48780060',0x400986ca:'4879413456bc',0x400e64de:'0c8400010000',0x400e64f2:'48794be37280',
 0x400ebc68:'206f0004202f0008',0x400ebc96:'4e75',0x400f09bc:'4ebaff96',0x400f09c8:'4eb9400ec23c',0x40102ae6:'4ef9400ec23c',
 0x400efc74:'203c4199d50c',0x400efc7a:'23c0431dc4c0',0x400efed6:'2679431dc4c0',0x400efede:'2688',0x400efee0:'2679431dc4c0',0x400efee6:'2688',0x400efee8:'20b9431dc4c0',0x400eff72:'b5f9431dc4c0',0x400f0006:'2079431dc4c0',0x400f0012:'2089',
}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
assert tuple(struct.unpack_from('>III',b,0x401fe594-base))==(0x419a38c0,0x41925eb8,0x429a38c0)
ring_addresses=[]
for initial in range(90):
    head=initial
    for frame in range(32):
        for ix in [head,head+90]:
            address=0x4199d224+4*ix
            assert 0x4199d224<=address and address+4<=0x4199d4f4
            assert not overlaps(address,4)
            ring_addresses.append(address)
        head+=1
        if head>89:head=0
    assert head==(initial+32)%90
# This counterexample checks the proof dependency, not a demonstrated runtime
# producer: an out-of-range initial head would write before wrap correction.
bad_index_witness=0x4199d224+4*(97+90)
assert bad_index_witness==marker[0] and overlaps(bad_index_witness,4)
work_copies=[]
for track in range(8):
    track_base=0x4199d024+0x40*track
    for lane in range(2):
        address=track_base+(0x20 if lane==0 else 0)
        assert 0x4199d024<=address and address+0x20<=0x4199d224
        assert not overlaps(address,0x20)
        work_copies.append(address)
scratch_writes=[0x8000f270+frame*0x30+field for frame in range(32) for field in range(0,0x30,4)]
assert all(not overlaps(a,4) and a+4<=0x8000f870 for a in scratch_writes)
startup=(0x40242000,0x431dc690)
assert (startup[1]-startup[0])%16==0 and startup[0]<=marker[0]<marker[1]<=startup[1]
intervals=[
 dict(name='fixed neighbor snapshot copy',site='400ef7fe',start='4199cd24',end_exclusive='4199cf24',basis='Three literal arguments, length 0x200'),
 dict(name='eight-track two-lane work-copy destinations',site='400ef514',start='4199d024',end_exclusive='4199d224',basis='Fixed backing base, 8 iterations, 0x40 outer stride; 2 inner 0x20 lanes'),
 dict(name='two-channel ring internal writes',sites=['400f025e','400f0270'],start='4199d224',end_exclusive='4199d4f4',basis='Head 0..89, second channel +90, 4-byte units; output argument writes separate and unresolved'),
 dict(name='scratch fill/clear in recovered caller routes',sites=['400f018e','400f01ea'],start='8000f270',end_exclusive='8000f870',basis='Both recovered callers pass 8000f270; at most 32 frames of 0x30 bytes'),
 dict(name='managed heap',start='419a38c0',end_exclusive='429a38c0',basis='Initialized allocator configuration; valid bounded allocations only'),
 dict(name='heap bitmap',start='41925eb8',end_exclusive='41945eb8',basis='Valid 0x100000 allocation units; unchecked corrupted indices not certified'),
 dict(name='scheduler nodes',start='4199d594',end_exclusive='4199da94',basis='64 nodes, 0x14 stride'),
 dict(name='event pool',start='4199da94',end_exclusive='4199fe94',basis='128 events, 0x48 stride'),
 dict(name='ordinary live queue node pool',start='431dbfb8',end_exclusive='431dc4b8',basis='64 nodes, 0x14 stride; sentinel not a pool member'),
]
for x in intervals:
    assert not overlaps(int(x['start'],16),int(x['end_exclusive'],16)-int(x['start'],16))
candidate=json.loads(pathlib.Path('work/marker-pointer-candidate-traces.json').read_text())
targets={int(x,16) for x in candidate['searched_targets']}
transfers=[]
for off in range(0,0x170000-6,2):
    op=int.from_bytes(b[off:off+2],'big');a=base+off;t=None;kind=None
    if op in (0x4eb9,0x4ef9):t=int.from_bytes(b[off+2:off+6],'big');kind='call' if op==0x4eb9 else 'tail'
    elif op in (0x4eba,0x4efa,0x6100,0x6000):t=a+2+int.from_bytes(b[off+2:off+4],'big',signed=True);kind='call' if op in (0x4eba,0x6100) else 'tail'
    elif op&0xff00 in (0x6000,0x6100) and op&255 not in (0,255):t=a+2+int.from_bytes(b[off+1:off+2],'big',signed=True);kind='tail' if op&0xff00==0x6000 else 'call'
    if t in targets:transfers.append(dict(site=f'{a:08x}',target=f'{t:08x}',kind=kind))
end_refs=[dict(literal=f'{base+m.start():08x}',instruction=f'{base+m.start()-2:08x}') for m in re.finditer(re.escape(struct.pack('>I',0x431dc4c0)),b)]
paths=[pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),pathlib.Path('work/section-3.bin')]
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
result=dict(read_only=True,global_storage_certified=False,firmware_guard_implemented=False,marker_start=f'{marker[0]:08x}',marker_end_exclusive=f'{marker[1]:08x}',verified_byte_anchors={f'{a:08x}':h for a,h in anchors.items()},bounded_disjoint_intervals=intervals,startup_overlap=dict(routine='400004b2',caller='40000542',start=f'{startup[0]:08x}',end_exclusive=f'{startup[1]:08x}',overlaps_marker=True),range_checks=dict(valid_ring_initial_heads=90,ring_word_stores_checked=len(ring_addresses),work_copy_ranges_checked=len(work_copies),scratch_word_positions_checked=len(scratch_writes),invalid_head_counterexample=dict(initial_head=97,second_channel_index=187,store_site='400f0270',address=f'{bad_index_witness:08x}',runtime_producer_established=False)),end_pointer_literal_consumers=end_refs,candidate_scan_summary=dict(searched_targets=candidate['searched_targets'],bulk_call_candidates=len(candidate['bulk_calls']),statuses=dict(Counter(c['status'] for c in candidate['bulk_calls'])),nearby_constant_store_candidates=len(candidate['nearby_constant_stores']),overlapping_constant_store_candidates=sum(c['overlaps_marker'] for c in candidate['nearby_constant_stores'])),candidate_bulk_calls=[{k:v for k,v in c.items() if k!='context'} for c in candidate['bulk_calls']],encoded_direct_transfer_candidates=transfers,manual_extent_resolutions=[dict(site='400986d0',destination='413456bc',length=0x60,disjoint=True),dict(site='400d93fc',destination='431a4044',length=0x100,disjoint=True),dict(site='400e64f8',destination='4be37280',max_length=0x10000,disjoint=True)],limitations=candidate['limitations']+['Ring output argument has no recovered caller; its destination remains unknown','No complete interprocedural points-to proof or global index ownership proof','No hardware DMA/bus-master destination audit'],unchanged_input_sha256=dict(zip([p.name for p in paths],hashes)))
pathlib.Path('outputs/Digitone-marker-pointer-and-bulk-write-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(anchors=len(anchors),ring_checks=len(ring_addresses),work_copy_ranges=len(work_copies),scratch_word_positions=len(scratch_writes),bulk_candidates=len(candidate['bulk_calls']),direct_transfers=dict(Counter(x['kind'] for x in transfers)),hashes_unchanged=True),indent=2))
