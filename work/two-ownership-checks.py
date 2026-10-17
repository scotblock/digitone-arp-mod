exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for start,end in [(0x400efa20,0x400efb00),(0x400ef810,0x400efa20),(0x4009e3cc,0x4009e480),(0x4009713c,0x4009719e),(0x4009deba,0x4009df4a)]:
 out.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
# Literal discovery is not whole-program pointer provenance.
for v in range(0x41345ee8,0x41346028,4):
 needle=struct.pack('>I',v);hits=[];p=0
 while True:
  p=b.find(needle,p)
  if p<0:break
  hits.append(hex(base+p));p+=1
 if hits:out.append(f'LITERAL {v:08x}: {hits}')
pathlib.Path('work/two-ownership-checks.txt').write_text('\n'.join(out))
print('\n'.join(out))

import json,hashlib
conditions={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
graphs=[]
for name,start,end in [('raw_live_producer',0x400efa20,0x400efc4e),('arp_global_reset',0x4009713c,0x4009719e),('cache_global_reset',0x400ef9d0,0x400ef9f6),('cache_track_reset',0x400ef9f6,0x400efa20),('event_copy',0x400f0690,0x400f06d4),('event_release',0x400f065c,0x400f0690)]:
 todo=[start];seen={};calls=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  assert start<=a<end,(name,hex(a))
  i=next(md.disasm(b[a-base:a-base+16],a,count=1));m=i.mnemonic.split('.')[0]
  assert i.id!=0 or bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)]
  seen[a]={'bytes':i.bytes.hex(),'instruction':f'{i.mnemonic} {i.op_str}'}
  if m=='rts':continue
  if m=='jmp':
   assert name=='raw_live_producer' and i.op_str=='$400f0886.l'
   calls.append({'site':hex(a),'instruction':f'{i.mnemonic} {i.op_str}'});continue
  if m in ('jsr','bsr'):calls.append({'site':hex(a),'instruction':f'{i.mnemonic} {i.op_str}'})
  if m in conditions|{'bra'}:
   todo.append(int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16))
   if m!='bra':todo.append(a+i.size)
  else:todo.append(a+i.size)
 graphs.append({'name':name,'instructions':{hex(a):v for a,v in sorted(seen.items())},'calls':calls})
assert all(not g['calls'] for g in graphs[1:4])
anchors={0x400dc5c8:'4eb9400f05d6',0x400dc5e8:'2d40fff8',0x400dc68a:'486effd0',0x400dc68e:'4eb9400efa20',0x400dc21c:'48780030',0x400dc220:'42a7',0x400dc244:'2d40ffdc',0x400dc25a:'4eb9400efa20',0x400efa90:'296a00280038',0x400efab8:'4294',0x400efbe0:'4e95',0x400efc08:'4e95',0x400efc2a:'4eb9400ec23c',0x4009de40:'4eb9400f0690',0x4009ce3c:'4eb9400f0690',0x400f069c:'4a92',0x400f06a8:'4ebaff4e',0x400f06ba:'5290',0x4009cef6:'4eb9400f065c',0x40094516:'40c2',0x40094518:'46fc2700',0x40094556:'4eb94009bd6a',0x40094562:'46c2'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),b[a-base:a-base+len(bytes.fromhex(h))].hex(),h)

# Executable ownership specification, not firmware execution. Every operation
# changes explicit owners as well as reference counts, permitting a negative
# test of raw replay without declaring that trace reachable in stock firmware.
class Pool:
 def __init__(self):self.refs=[0]*64;self.free=set(range(64))
 def pop(self):
  s=min(self.free);self.free.remove(s);self.refs[s]+=1;return s
 def retain(self,s):self.refs[s]+=1
 def release(self,s):
  assert self.refs[s]>0
  self.refs[s]-=1
  if self.refs[s]==0:self.free.add(s)
 def consistent(self,owners):
  return all(self.refs[s]==owners.count(s) and ((s in self.free)==(self.refs[s]==0)) for s in range(64))
def replace(p,dest,src):
 if dest is not None:p.release(dest)
 if src is not None:p.retain(src)
 return src
tests=[]
def check(n,c):assert c,n;tests.append(n)
p=Pool();s=p.pop();queue=[s];template=None
check('initial pop transfers one reference to one queued owner',p.consistent(queue))
template=replace(p,template,queue[0])
check('template capture adds a second reference',p.consistent(queue+[template]))
p.release(queue.pop())
check('event release leaves template live with empty queue',p.consistent([template]) and p.refs[s]==1 and s not in p.free)
t=p.pop();queue=[t];template=replace(p,template,t)
check('template replacement frees old record and retains new',p.consistent(queue+[template]) and s in p.free)
p.release(queue.pop());template=replace(p,template,None)
check('explicit payload-only template cleanup restores 64 free records',p.consistent([]) and len(p.free)==64)
# Four tracks retain different records even after a complete queue drain.
p=Pool();queue=[p.pop() for _ in range(4)];templates=[replace(p,None,s) for s in queue]
for s in queue:p.release(s)
queue=[]
check('four-track drain leaves four retained records',p.consistent(templates) and len(p.free)==60)
for s in templates:p.release(s)
check('cleanup of all four templates restores pool',p.consistent([]) and len(p.free)==64)
# Replay from a borrowed cache is a COUNTEREXAMPLE to a generic ownership
# contract. Eligibility of this exact state in actual firmware is unproven.
p=Pool();s=p.pop();template=replace(p,None,s);p.release(s)
queue=[s]
check('raw replay without retain fails owner accounting',not p.consistent(queue+[template]))
template=replace(p,template,s)
check('same-record overwrite with missing source retain leaves live free-list entry',s in p.free and p.refs[s]==1 and not p.consistent(queue+[template]))
# A proper retain before replay prevents that intermediate zero count.
p=Pool();s=p.pop();template=replace(p,None,s);p.release(s);p.retain(s);queue=[s]
template=replace(p,template,s)
check('retained replay balances same-record replacement',p.consistent(queue+[template]) and s not in p.free)
p.release(queue.pop());p.release(template)
check('retained replay finishes with all records free',p.consistent([]) and len(p.free)==64)

source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r={'firmware_modified':False,'hashes_unchanged':True,'sha256':hashes,'anchors':{hex(a):h for a,h in anchors.items()},'confirmed_local_graphs':graphs,'specification_checks':tests,'model_limit':'Not firmware emulation. Negative cached-replay trace has not been proved reachable.','raw_copy_status':'Normal fresh-record handoff recovered; cached replay eligibility and allocation-failure ownership unresolved.','reset_status':'Template overwrite releases old record; audited arp/cache resets do not release retained templates. Empty queue cannot certify pool reinitialization.','event_type_width':'32-bit long at offset 0; earlier word shorthand was inaccurate.'}
pathlib.Path('outputs/Digitone-two-ownership-checks-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs),'anchors':len(anchors),'specification_checks':len(tests),'hashes_unchanged':True},indent=2))
