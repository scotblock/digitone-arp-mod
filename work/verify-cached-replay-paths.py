"""Read-only instruction graphs and a branch/ownership specification."""
exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
cond={'beq','bne','bgt','bge','blt','ble','bcs','bcc','bhi','bls','bpl','bmi','bvc','bvs'}
graphs=[]
for name,start,end in [('live_note_input',0x400dc432,0x400dc8c4),('cache_builder',0x400efa20,0x400efc4e),('event_allocation',0x400f0626,0x400f065c),('step_setter',0x400dcaf6,0x400dcb0e),('step_selection',0x400ab0ac,0x400ab160),('selection_disable',0x400aa892,0x400aa8e0),('mode_setter',0x4002f08a,0x4002f10a),('selector_setter',0x4002f13a,0x4002f1b0),('synth_track_predicate',0x4009e39e,0x4009e3ac),('fallback_settings',0x4009c2f8,0x4009c314),('midi_channel_route',0x400dc758,0x400dc8c4),('midi_note_on_entry',0x400dc8c4,0x400dc90c)]:
 todo=[start];seen={};calls=[];returns=[]
 while todo:
  a=todo.pop()
  if a in seen:continue
  if name=='midi_note_on_entry' and a==0x400dc3e2:
   calls.append({'tail':True,'instruction':'velocity-zero branch to recovered note-off entry 400dc3e2'});continue
  assert start<=a<end,(name,hex(a))
  i=next(md.disasm(b[a-base:a-base+16],a,count=1));m=i.mnemonic.split('.')[0]
  assert i.id!=0 or bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)],(name,hex(a),i.mnemonic)
  seen[a]={'bytes':i.bytes.hex(),'instruction':f'{i.mnemonic} {i.op_str}'}
  if m=='rts':returns.append(hex(a));continue
  if m=='jmp':calls.append({'site':hex(a),'tail':True,'instruction':f'{i.mnemonic} {i.op_str}'});continue
  if m in ('jsr','bsr'):calls.append({'site':hex(a),'instruction':f'{i.mnemonic} {i.op_str}'})
  if m in cond|{'bra'}:
   todo.append(int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16))
   if m!='bra':todo.append(a+i.size)
  else:todo.append(a+i.size)
 graphs.append({'name':name,'instructions':{hex(a):v for a,v in sorted(seen.items())},'calls':calls,'returns':returns})
anchors={0x400dc598:'b2b9401feafc',0x400dc59e:'650000de',0x400dc5bc:'6606',0x400dc5c8:'4eb9400f05d6',0x400dc5e8:'2d40fff8',0x400dc68e:'4eb9400efa20',0x400efaf8:'6542',0x400efb8a:'660000b8',0x400efbc8:'677a',0x400efbf2:'6750',0x400efc1a:'6728',0x400efc08:'4e95',0x400efc2a:'4eb9400ec23c',0x400f0634:'670a',0x400f0644:'6712',0x400f0658:'2008',0x400dcb06:'23c0401feafc',0x400ab0b8:'24280158',0x400ab0bc:'2628015c',0x400ab14c:'4ef9400dcaf6',0x400aa8c2:'4878ffff',0x400aa8c6:'4eb9400dcaf6',0x40044630:'4eb9400ab0ac',0x4002f0e4:'2142012a',0x4002f180:'2142012e'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),b[a-base:a-base+len(bytes.fromhex(h))].hex(),h)
assert struct.unpack_from('>i',b,0x401feafc-base)[0]==-1
channel=next(g for g in graphs if g['name']=='midi_channel_route')
assert channel['instructions']['0x400dc80e']['bytes']=='4bfa fc22'.replace(' ','')
assert channel['instructions']['0x400dc898']['bytes']=='4e95'
assert not any('400dcaf6' in c['instruction'] or '400aa892' in c['instruction'] for c in channel['calls'])

def direct_refs(target):
 refs=[]
 for off in range(0,len(b)-6,2):
  op=struct.unpack_from('>H',b,off)[0]
  if op in (0x4eb9,0x4ef9) and struct.unpack_from('>I',b,off+2)[0]==target:refs.append(hex(base+off))
  if op>>8 in (0x60,0x61):
   disp=op&255
   if disp==0:disp=struct.unpack_from('>h',b,off+2)[0]
   elif disp==255:disp=struct.unpack_from('>i',b,off+2)[0]
   elif disp>=128:disp-=256
   if base+off+2+disp==target:refs.append(hex(base+off))
 return refs
refs={hex(t):direct_refs(t) for t in [0x400dcaf6,0x400dcb0e,0x400ab0ac]}
assert refs['0x400dcaf6']==['0x400aa8c6','0x400ab14c']

# This specification uses recovered decisions and addresses; it does not
# execute ColdFire code or establish hardware/controller event interleaving.
class Cache:
 def __init__(self,mode,selector,step):
  self.mode=mode;self.selector=selector;self.step=step;self.active=[];self.selected=None;self.cache={};self.refs={};self.queue=[];self.next=0;self.trace=[]
 def select(self):
  if not self.active:return None
  if self.selector==1:return min(self.active)
  if self.selector==2:return max(self.active)
  return self.active[-1]
 def allocate_payload(self):
  if not 0<=self.step<=63:return None
  p=self.next;self.next+=1;self.refs[p]=1;return p
 def publish(self,n,site):
  p=self.cache[n];self.queue.append((n,p));self.trace.append({'site':site,'note':n,'payload':p,'refs':None if p is None else self.refs[p]})
 def press(self,n,event_available=True):
  p=self.allocate_payload();self.cache[n]=p
  if n in self.active:self.active.remove(n)
  self.active.append(n)
  if self.mode<=1:self.selected=n
  else:
   choice=self.select()
   if choice!=n:self.trace.append({'site':'400efb8a -> 400efc44','note':n,'payload':p,'unselected':True});return
   self.selected=n
  if event_available:self.publish(n,'400efc2a -> 400f0886')
  else:self.trace.append({'site':'400efc1a -> 400efc44','note':n,'payload':p,'event_allocation_failed':True})
 def release_note(self,n,first_event=True,second_event=True):
  # Zeroed note-off descriptor overwrites the departing slot before selection.
  self.cache[n]=None
  old=self.selected
  if n in self.active:self.active.remove(n)
  if self.mode<=1:
   self.selected=None
   if first_event:self.publish(n,'400efc2a -> 400f0886')
   return
  chosen=self.select()
  self.selected=chosen
  if chosen is not None and chosen!=old:
   if not first_event:self.trace.append({'site':'400efbc8 -> 400efc44','event_allocation_failed':True});return
   self.publish(n,'400efbe0 -> 400efbe4')
   if not second_event:self.trace.append({'site':'400efbf2 -> 400efc44','event_allocation_failed':True});return
   self.publish(chosen,'400efc08 -> 400f0886')
  elif first_event:self.publish(n,'400efc2a -> 400f0886')
 def consume_without_arp(self):
  # Normal event release applies even with arp disabled. No retained template.
  for n,p in self.queue:
   if p is not None:self.refs[p]=(self.refs[p]-1)&0xffffffff
  self.queue=[]

checks=[];cases=[]
def check(n,c):assert c,n;checks.append(n)
def save(n,c):cases.append({'name':n,'trace':c.trace,'references':c.refs,'cache':c.cache})
for mode in [2,3]:
 for selector,first,second in [(0,60,64),(1,64,60),(2,60,64)]:
  c=Cache(mode,selector,0);c.press(first);c.press(second)
  old=c.cache[first];c.consume_without_arp();c.release_note(second)
  check(f'mode {mode} selector {selector}: replay pointer non-null after prior release',c.queue[-1]==(first,old) and c.refs[old]==0)
  c.consume_without_arp()
  check(f'mode {mode} selector {selector}: modeled release underflows stale reference',c.refs[old]==0xffffffff)
  save(f'already-published replay mode {mode} selector {selector}',c)
for selector,first,second in [(1,60,64),(2,64,60)]:
 c=Cache(2,selector,0);c.press(first);c.press(second);p=c.cache[second]
 check(f'selector {selector}: unselected cache keeps initial reference',c.refs[p]==1 and len(c.queue)==1)
 c.release_note(first)
 check(f'selector {selector}: first replay of unpublished cache transfers reference',c.queue[-1]==(second,p) and c.refs[p]==1)
 save(f'unselected first transfer selector {selector}',c)
 c=Cache(2,selector,0);c.press(first);c.press(second);p=c.cache[second];c.release_note(second)
 check(f'selector {selector}: departure before publication drops pointer with positive ref',c.cache[second] is None and c.refs[p]==1)
 save(f'unselected departure selector {selector}',c)
c=Cache(2,0,0);c.press(60,event_available=False);p=c.cache[60]
check('failed fresh-event allocation preserves non-null cache and initial reference',not c.queue and c.refs[p]==1 and c.cache[60]==p)
c.release_note(60)
check('departure after failed publication discards pointer without modeled release',c.cache[60] is None and c.refs[p]==1)
save('fresh-event failure then departure',c)
for first_event,second_event,expected in [(False,True,0),(True,False,1)]:
 c=Cache(2,0,0);c.press(60);c.press(64);c.consume_without_arp();c.release_note(64,first_event,second_event)
 check(f'replay allocation failure {first_event}/{second_event}: partial publication count',len(c.queue)==expected)
 save(f'replay allocation failure {first_event}/{second_event}',c)
for mode in range(4):
 for selector in range(3):
  c=Cache(mode,selector,-1);c.press(60);c.press(64);c.release_note(64)
  check(f'initial step sentinel mode {mode} selector {selector}: no cache payload',all(p is None for p in c.cache.values()) and not c.refs)
for mode in [0,1]:
 c=Cache(mode,0,0);c.press(60);c.press(64);c.consume_without_arp();c.release_note(64)
 check(f'mode {mode}: no alternate-note replay on departure',len(c.queue)==1 and c.queue[0][1] is None)
source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r={'firmware_modified':False,'sha256':hashes,'confirmed_local_graphs':graphs,'verified_anchors':{hex(a):h for a,h in anchors.items()},'step_setter_direct_candidates':refs,'step_initial_value':-1,'step_setter_valid_range':'-1 or 0..63','settings_valid_ranges':{'12a':'0..3','12e':'0..2'},'specification_checks':checks,'scenarios':cases,'limits':['Branch-level eligibility established; complete controller/interleaving reachability not established.','Ownership scenarios are specifications, not execution of firmware.','Exact UI labels for mode/selector fields remain unverified.','Direct-reference scan does not certify absence of computed aliases.']}
pathlib.Path('outputs/Digitone-cached-replay-eligibility-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'graphs':len(graphs),'instructions':sum(len(g['instructions']) for g in graphs),'anchors':len(anchors),'checks':len(checks),'scenarios':len(cases),'hashes_unchanged':True},indent=2))
