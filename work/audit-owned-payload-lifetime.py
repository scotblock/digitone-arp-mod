"""Read-only, confirmed-entry local CFGs and PC lifecycle specifications."""
exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib,random
conditions={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
functions=[('parameter_producer',0x40093bd4,0x40093c26),('parameter_consumer',0x4009b600,0x4009b69e),('payload_pop',0x400f05d6,0x400f05f8),('payload_release',0x400f05f8,0x400f0626),('event_release',0x400f065c,0x400f0690),('event_copy',0x400f0690,0x400f06d4),('pool_initializer',0x400f0504,0x400f05d6)]
graphs=[]
for name,start,end in functions:
 todo=[start];seen={};calls=[];returns=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  assert start<=a<end,(name,hex(a))
  i=next(md.disasm(b[a-base:a-base+16],a,count=1));m=i.mnemonic.split('.')[0]
  # Capstone's unsupported TST address-register encodings are known 2-byte
  # instructions that fall through; never consume a provisional window.
  assert i.id!=0 or bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)]
  seen[a]=dict(bytes=i.bytes.hex(),instruction=f'{i.mnemonic} {i.op_str}')
  if m=='rts':returns.append(a);continue
  if m in {'jmp','rte','illegal','trap'}:raise AssertionError((name,hex(a),m))
  if m in {'jsr','bsr'}:calls.append(dict(site=hex(a),instruction=f'{i.mnemonic} {i.op_str}'))
  if m in conditions|{'bra'}:
   t=int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16);todo.append(t)
   if m!='bra':todo.append(a+i.size)
  else:todo.append(a+i.size)
 graphs.append(dict(name=name,start=hex(start),end_exclusive=hex(end),instructions={hex(a):v for a,v in sorted(seen.items())},calls=calls,normal_returns=[hex(x) for x in returns]))
assert all(not x['calls'] for x in graphs[:4])
anchors={0x40093bd4:'4feffff4',0x40093c04:'45f12814',0x40093c08:'3481',0x40093c0a:'35500002',0x40093c12:'744f',0x40093c18:'23400008',0x4009b61a:'246f0034',0x4009b626:'41ea0014',0x4009b648:'b2aa0008',0x4009b680:'5088',0x4009b682:'3d95ca02',0x4009b68e:'27830c00',0x4009dc88:'4bf94009b600',0x4009dd2e:'4e95',0x4009e20a:'4eb94009b600',0x400f05ee:'42a80010',0x400f05f2:'5290',0x400f0608:'2081',0x400f061a:'21400010',0x400f061e:'23c84199fe98',0x400f06ba:'5290',0x400f06c4:'4eb9400ec23c',0x4009bdb4:'42aa0038',0x4009bde8:'2f0b',0x4009bdec:'4ebafeca',0x4009bcec:'4ebaffca'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
stride=0x504;pool=64*stride;trailer=bytearray(b'OWNED-TRAILER-16');assert len(trailer)==16
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
check('79-entry producer maximum count',max(range(80))==79)
for slot in range(64):
 start=slot*stride
 for count in range(80):
  for entry in range(count):
   check_addr=start+20+entry*8
   assert check_addr+4<=start+stride and check_addr+4<=pool
check('all 64 slots and counts 0..79 exclude trailer',True)
check('maximum producer end within record',20+78*8+4==0x288 and 0x288<=stride)
# Recovered consumer loads two words at offsets 0 and 2 then advances 8.
check('consumer reads same bounded entries',20+78*8+4<=stride)
# Specification free list, not execution of the stock routines.
free=list(range(64));refs=[0]*64;memory=bytearray(pool)+trailer;trace=[]
def store_header(slot,off,value):
 assert off in (0,16)
 memory[slot*stride+off:slot*stride+off+4]=struct.pack('>I',value&0xffffffff)
def pop():
 if not free:raise RuntimeError('stock null-head dereference is outside valid lifecycle')
 slot=free.pop(0);refs[slot]+=1;store_header(slot,16,0);store_header(slot,0,refs[slot]);return slot
def retain(slot):refs[slot]+=1;store_header(slot,0,refs[slot])
def release(slot):
 assert refs[slot]>0
 refs[slot]-=1;store_header(slot,0,refs[slot])
 if refs[slot]==0:store_header(slot,16,free[0]*stride if free else 0);free.insert(0,slot)
live=[pop() for _ in range(64)]
check('64 allocations return ordinary records only',set(live)==set(range(64)))
try:pop();raise AssertionError('unexpected 65th record')
except RuntimeError:check('exhaustion never returns trailer as record',True)
for slot in live:retain(slot)
for slot in live:release(slot)
check('retained event keeps record out of free list',not free and all(x==1 for x in refs))
random.Random(142).shuffle(live)
for slot in live:release(slot)
check('all final releases return precisely 64 records',len(free)==64 and set(free)==set(range(64)))
for cycle in range(32):
 slot=pop();retain(slot);release(slot);release(slot)
 assert memory[pool:]==trailer
check('copy release recycling preserves trailer',memory[pool:]==trailer)
def may_reinitialize(quiescent,busy_depth,live_records):return quiescent and busy_depth==0 and live_records==0
check('reset blocked with retained records',not may_reinitialize(True,0,1))
check('reset blocked with active pattern transaction',not may_reinitialize(True,1,0))
check('reset blocked without quiescence',not may_reinitialize(False,0,0))
check('quiescent reset specification allowed',may_reinitialize(True,0,0))
# Confirmed *extra* wrapper route; no external caller of this test-like routine
# was found in direct entry discovery. Do not label it definitely unreachable.
refs_to_wrapper=[];refs_to_test=[]
for off in range(0,len(b)-8,2):
 a=base+off;op=int.from_bytes(b[off:off+2],'big');dst=None
 if op in (0x4eb9,0x4ef9):dst=int.from_bytes(b[off+2:off+6],'big')
 elif op in (0x4eba,0x4efa):dst=a+2+int.from_bytes(b[off+2:off+4],'big',signed=True)
 elif op&0xf000==0x6000:
  lo=op&255;disp=int.from_bytes(b[off+2:off+(6 if lo==255 else 4)],'big',signed=True) if lo in (0,255) else int.from_bytes(b[off+1:off+2],'big',signed=True);dst=a+2+disp
 if dst==0x4009bcb8:refs_to_wrapper.append(hex(a))
 if dst==0x4009bde8:refs_to_test.append(hex(a))
assert refs_to_wrapper==['0x4009bcec','0x4009bdec'] and refs_to_test==[]
source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r=dict(read_only=True,firmware_modified=False,scope='Recovered parameter producer, playback consumer, payload free list, common event copy/release, pool initializer',local_graphs=graphs,verified_anchors={hex(a):h for a,h in anchors.items()},pc_specification_checks=checks,wrapper_calls=refs_to_wrapper,test_like_routine=dict(entry='4009bde8',external_direct_transfers_found=refs_to_test,reachability='Unresolved; not certified unreachable'),producer_max_entries=79,producer_write_end_exclusive='record+0x288',record_bytes=stride,owner_lifetime_status='No enclosing allocation free on audited record release routes; complete global pointer escape/free provenance remains open',limitations=['Confirmed-entry CFGs treat calls as returning normally','Producer and consumer bounds depend on valid pointers/counts from recovered creator','Candidate field-offset scans include unrelated objects and are not a complete whole-image typed event map','Stock exhaustion/null-init and live reinitialization not safe by these models','No hooks or hardware validation performed'],remaining=['Confirm other payload-pointer escapes and typed event sources','Close reachability/quiescence of extra initialization route','Design exact initializer integration and failure continuation'],unchanged_sha256=dict(syx=hashes[0],decoded_section_3=hashes[1]))
pathlib.Path('outputs/Digitone-owned-payload-lifetime-audit-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(functions=len(graphs),reachable_instructions=sum(len(x['instructions']) for x in graphs),anchors=len(anchors),model_checks=len(checks),wrapper_calls=refs_to_wrapper,hashes_unchanged=True),indent=2))
