"""PC-only specification checks and byte evidence; no firmware patching."""
exec(open('work/disassemble.py').read().split('out=[]')[0])
import json,hashlib,random
anchors={
0x4009bcb8:'4878009e',0x4009bcbc:'4eb9400f0504',
0x400f056a:'e78a',0x400f056c:'068200000014',0x400f0572:'4ab94199d590',0x400f0578:'6622',0x400f057a:'2602',0x400f057c:'ed8b',0x400f057e:'2f03',0x400f0580:'4eb9400dab8c',0x400f058c:'23c04199d590',0x400f0592:'4eb9400ec284',0x400f059e:'20394199d590',0x400f05ba:'2202',0x400f05be:'ed89',0x400f05c6:'9282',0x400f05ca:'42a80010',
0x400dab8c:'4fefffd4',0x400dac32:'7010',0x400dac3c:'5381',0x400dac3e:'04c1',0x400dac40:'701c',0x400dac4e:'9081',0x400dac50:'e1aa',0x400dad22:'41f228ff',0x400dad38:'01d0',0x400da9f0:'4280',0x400dadb0:'00fffff0',
0x40093e90:'4eb9400f05d6',0x400dc5c8:'4eb9400f05d6',0x40093bd4:'4feffff4',0x40093bec:'4281',0x40093bf4:'4280',0x40093c02:'e78a',0x40093c04:'45f12814',0x40093c08:'3481',0x40093c0a:'35500002',0x40093c12:'744f',0x40093c16:'66de',
0x4009bcec:'4ebaffca',0x4009bd08:'4eb9400f00ea',0x4009bd52:'23c0400002fc',
}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
cfg=struct.unpack_from('>IIIIII',b,0x401fe590-base)
assert cfg==(0,0x419a38c0,0x41925eb8,0x429a38c0,20,0x100000)
def rounded(n):return 1<<(max(n,16)-1).bit_length()
stride=8*158+20;pool=64*stride;trailer=16;newrequest=pool+trailer
assert (stride,pool,newrequest)==(0x504,0x14100,0x14110)
assert rounded(pool)==rounded(newrequest)==0x20000
checks=[]
def checked(name,condition):
 assert condition,name
 checks.append(name)
checked('request explicitly includes trailer',newrequest>pool and pool+trailer==newrequest)
checked('allocator rounded footprint unchanged',rounded(pool)==rounded(newrequest))
checked('16-byte aligned trailer offset',pool%16==0)
checked('last record ends at trailer start',63*stride+stride==pool)
checked('all record capacities exclude trailer',all(slot*stride+20+8*158<=pool for slot in range(64)))
checked('all header writes exclude trailer',all(slot*stride+offset+4<=pool for slot in range(64) for offset in (0,4,8,12,16)))
checked('79-entry recovered producer excludes trailer',all(slot*stride+20+entry*8+4<=pool for slot in range(64) for entry in range(79)))
# A specification allocator that protects the entire rounded block, not the
# stock implementation executed in an emulator.
heapbase=cfg[1];heapend=cfg[3]
for offset in range(0,heapend-heapbase-rounded(newrequest)+1,rounded(newrequest)):
 p=heapbase+offset
 assert p%16==0 and p+newrequest<=heapend and p+rounded(newrequest)<=heapend
checked('all 128 aligned whole-block placements fit heap',True)
mem=bytearray(rounded(newrequest));canary=b'TRAILER-OWNED-16';assert len(canary)==16
mem[pool:pool+16]=canary
slots=list(range(64));random.Random(142).shuffle(slots)
for cycle in range(32):
 for slot in slots:
  start=slot*stride
  mem[start:start+stride]=bytes([(slot+cycle)&255])*stride
 assert mem[pool:pool+16]==canary
checked('2048 full-capacity recycled record writes preserve trailer',True)
# Readiness protocol is a proposal, not existing firmware functionality.
def usable(pointer,phase,depth=0,poison=False):
 return pointer is not None and phase=='READY' and depth==0 and not poison
checked('null owner disables capture',not usable(None,'READY'))
checked('published pointer during clearing disables capture',not usable(heapbase,'UNREADY'))
checked('partial trailer initialization disables capture',not usable(heapbase,'INITIALIZING'))
checked('completed trailer initialization enables capture',usable(heapbase,'READY'))
checked('writer depth excludes snapshot',not usable(heapbase,'READY',1))
checked('fault latch excludes snapshot',not usable(heapbase,'READY',0,True))
checked('reinitialization requires invalidation and quiescence',not usable(heapbase,'UNREADY'))
# A valid buddy allocation marks its last 16-byte unit, outside the requested
# trailer, at the rounded block boundary; distinguish that bitmap write from
# free-list/footer data inside *free* blocks.
checked('trailer precedes rounded allocation boundary',pool+16<rounded(newrequest))
# Direct-transfer candidate inventory for narrow allocator/pool dependencies.
targets={0x400f0504:[],0x400f05d6:[],0x400f05f8:[]}
for off in range(0,len(b)-8,2):
 op=int.from_bytes(b[off:off+2],'big');a=base+off;dst=None
 if op in (0x4eb9,0x4ef9):dst=int.from_bytes(b[off+2:off+6],'big')
 elif op in (0x4eba,0x4efa):dst=a+2+int.from_bytes(b[off+2:off+4],'big',signed=True)
 elif op&0xf000==0x6000:
  lo=op&255
  disp=int.from_bytes(b[off+2:off+(6 if lo==255 else 4)],'big',signed=True) if lo in (0,255) else int.from_bytes(b[off+1:off+2],'big',signed=True)
  dst=a+2+disp
 if dst in targets:targets[dst].append(hex(a))
assert targets=={0x400f0504:['0x4009bcbc'],0x400f05d6:['0x40093e90','0x400dc5c8'],0x400f05f8:['0x400f066e','0x400f06a8']}
source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r=dict(read_only=True,firmware_modified=False,flashable_output_produced=False,proposal='Explicit 16-byte trailer on persistent payload-pool allocation',owner_global='4199d590',trailer_address_expression='*(4199d590) + 0x14100',original_request=pool,proposed_request=newrequest,rounded_block_bytes=rounded(newrequest),record_stride=stride,record_count=64,verified_instruction_anchors={hex(a):h for a,h in anchors.items()},direct_transfer_candidates={hex(k):v for k,v in targets.items()},specification_checks=checks,model_limit='Arithmetic/layout/protocol specification, not emulator execution of firmware allocator or pool consumers',ownership_status='Promising explicit owned subregion; integration and complete payload consumer bounds not certified',remaining=['Audit all payload record users for upper bounds and escapes','Validate persistent owner lifetime and any reset/reinitialization path','Design null/cookie/readiness checks and cold initialization before audio publication','Audit hook register/stack liveness and writer cleanup','Confirm allocator behavior in executable emulation before hardware testing'],unchanged_sha256=dict(syx=hashes[0],decoded_section_3=hashes[1]))
pathlib.Path('outputs/Digitone-owned-storage-alternative-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(anchors=len(anchors),model_checks=len(checks),old_request=hex(pool),new_request=hex(newrequest),rounded_footprint=hex(rounded(newrequest)),hashes_unchanged=True),indent=2))
