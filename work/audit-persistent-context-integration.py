"""Read-only stock execution with external PC metadata observer, no patched code."""
exec(open('work/execute-cache-ordering.py').read().split('checks=[];cases=[]')[0])
ns={};exec(open('work/test-persistent-context-design.py').read().split('checks=[]')[0],ns)
Sidecar=ns['Sidecar'];Snapshot=ns['Snapshot'];key=ns['key']
# Use the actual fixed event addresses in this controlled RAM setup.
E=0x4199da94
RANGES.extend([(0x4009bd8a,0x4009bde8),(0x400efcb8,0x400f003a),(0x400f07ac,0x400f0886)])
source=' def run'+pathlib.Path('work/execute-payload-lifecycle.py').read_text().split(' def run',1)[1].split('\nP=',1)[0]
source=source.replace('   self.steps.append(pc)','   self.steps.append(pc)\n   if hasattr(self,"observe"): self.observe(pc)')
source=source.replace("   elif m=='st':self.put(ops[0],1,255)","   elif m=='sle':self.put(ops[0],1,255 if (self.sr&4 or bool(self.sr&8)^bool(self.sr&2)) else 0)\n   elif m=='st':self.put(ops[0],1,255)")
exec('if True:\n'+source);Machine.run=run
checks=[];cases=[]
def check(n,c):assert c,n;checks.append(n)

def attach(m):
 m.meta=Sidecar();m.context=None;m.observations=[];m.pending=[]
 def observe(pc):
  # Completed-copy observation precedes the actual publisher/link store.
  for record in list(m.pending):
   if pc==record['return']:
    dst=record['dst'];src=record['src'];dk=key(dst)
    if dk and dk[0]=='accepted':
     # A generic retained copy cannot authorize a new identity.
     m.meta.accepted.pop(dk[1],None)
    elif dk:m.meta.entries[dk]=record['snapshot']
    m.observations.append({'kind':'copy completed','pc':hex(pc),'dst':hex(dst),'src':hex(src),'snapshot':record['snapshot'].word() if record['snapshot'] else 0})
    m.pending.remove(record)
  if pc==0x400f0658:
   e=m.reg['a0']
   if e:m.meta.initialize(key(e))
   m.observations.append({'kind':'allocation result','event':hex(e)})
  if pc==0x400f0680:
   e=m.reg['a2'];m.meta.reclaim(key(e));m.observations.append({'kind':'pre-recycle invalidation','event':hex(e),'pc':hex(pc)})
  if pc==0x400efa5a:
   e=m.reg['a4'];d=m.reg['a2'];snap=m.context if m.read(d+12,4)==1 else None
   m.meta.initialize(key(e),snap)
   m.observations.append({'kind':'builder entry invalidation/capture assumption','event':hex(e),'snapshot':snap.word() if snap else 0})
  if pc==0x400ec23c:
   sp=m.reg['a7'];ret=m.read(sp,4);dst=m.read(sp+4,4);src=m.read(sp+8,4);length=m.read(sp+12,4)
   if length==72:
    m.pending.append({'return':ret,'dst':dst,'src':src,'snapshot':m.meta.candidate(key(src))})
  if pc==0x400efe8e:
   m.meta.initialize(key(m.reg['a0']))
  if pc==0x400efed6:
   node=m.reg['a0'];track=m.read(node+12,4);vel=m.read(node+8,4)
   m.meta.initialize(key(node),m.context if track<4 and vel>0 else None)
  if pc==0x400efede:
   node=m.reg['a0'];check('queue context initialized before first pending link',key(node) in m.meta.entries)
   m.observations.append({'kind':'queue first publication link','node':hex(node),'context':m.meta.candidate(key(node)).word() if m.meta.candidate(key(node)) else 0})
  if pc==0x400efff8:
   dst=m.reg['a0'];src=m.reg['a2'];m.meta.copy(key(dst),key(src))
   m.observations.append({'kind':'queue to event transfer before publication','node':hex(src),'event':hex(dst)})
  if pc in (0x400efecc,0x400f001e):
   node=m.reg['a0'] if pc==0x400efecc else m.reg['a2'];m.meta.reclaim(key(node))
   m.observations.append({'kind':'queue invalidation before free-list publication','node':hex(node)})
  if pc==0x400f07ac:
   e=m.read(m.reg['a7']+4,4)
   check('timed publisher sees completed metadata transfer',not m.pending and key(e) is not None)
   m.observations.append({'kind':'timed publisher entry','event':hex(e)})
  if pc==0x400f0886:
   e=m.read(m.reg['a7']+4,4)
   check('publisher sees fully completed byte/context copy',not m.pending and key(e) is not None)
   m.observations.append({'kind':'publication','event':hex(e),'context':m.meta.candidate(key(e)).word() if m.meta.candidate(key(e)) else 0})
  if pc==0x4009bdd2:
   check('clone context finished before first link mutation',not m.pending)
   m.observations.append({'kind':'clone first link store','event':hex(m.reg['a2'])})
 m.observe=observe
 return m

for selector,a,bnote in [(0,60,64),(1,64,60),(2,60,64)]:
 m=attach(setup(2,selector));A=Snapshot(0,0,0);B=Snapshot(2,5,0)
 m.context=A;emit(m,a,True);qa=queued(m)
 check('initial builder publication carries A',m.meta.candidate(key(qa[0]['event']))==A)
 consume(m);m.context=B;emit(m,bnote,True);consume(m)
 m.context=None;emit(m,bnote,False);q=queued(m)
 check('release invalidates its context',m.meta.candidate(key(q[0]['event'])) is None)
 check('old cache replay retains A across receiving-pattern change',m.meta.candidate(key(q[1]['event']))==A)
 check('release and replay contexts remain separate',q[0]['event']!=q[1]['event'])
 cases.append({'name':'actual builder/publisher press-consume-press-consume-release','selector':selector,'steps':len(m.steps),'trace':m.observations})

m=attach(setup());busy=[event(m) for _ in range(128)];m.context=Snapshot(5,5,0);emit(m,60,True)
check('actual exhausted allocator publishes nothing',not queued(m))
check('allocation failure still refreshes held candidate',m.meta.candidate(key(K+0x414+60*72))==m.context)
m.context=None;emit(m,60,False)
check('departure after allocation failure clears cached candidate',m.meta.candidate(key(K+0x414+60*72)) is None)
cases.append({'name':'actual builder allocation failure and departure','steps':len(m.steps),'trace':m.observations})

# Actual common-copy and remap helper, controlled contexts independent of payloads.
m=attach(setup());m.map(0x41345f08,4*72);m.map(0x419a304c,4*72)
e=event(m);A=Snapshot(0,0,0);m.meta.initialize(key(e),A)
m.write(e+4,4,1);m.write(e+8,4,0);m.write(e+60,4,0);m.write(e+64,4,17)
m.run(0x400f0690,(0x41345f08,e))
check('generic retained copy cannot invent accepted context',m.meta.pitch(0,17) is None)
# Dedicated caller adapter: acceptance is supplied, not executed in this case.
m.meta.accept(0,17,key(e));tick=event(m);m.run(0x400f0690,(tick,0x41345f08))
check('actual retained-to-event copy propagates accepted snapshot',m.meta.candidate(key(tick))==A)
m.run(0x4009bd8a,(tick,1));clone=m.read(tick+68,4)
check('actual remap clone preserves immutable capture source',m.meta.candidate(key(clone))==A and m.read(clone+8,4)==1 and m.read(clone+60,4)==0)
m.meta.accept(1,17,key(clone));B=Snapshot(2,5,1);m.meta.initialize(key(e),B);m.meta.accept(1,17,key(e))
check('continuing destination read independent of incoming copy context',m.meta.pitch(1,17)==B and m.meta.candidate(key(clone))==A)
m.meta.initialize(key(0x419a304c),B);out=event(m);m.run(0x400ec23c,(out,0x419a304c,72));m.observe(0xffffffff)
check('actual raw sequencer-cache copy transfers known candidate',m.meta.candidate(key(out))==B)
m.run(0x400f065c,(out,));again=event(m)
check('actual event recycle returns same slot with invalid metadata',again==out and m.meta.candidate(key(again)) is None)
cases.append({'name':'actual common copy, remap, raw copy and event recycling','steps':len(m.steps),'trace':m.observations})

# Complete actual delayed-note handler for notes-only descriptors, controlled RAM.
Q=0x431dbfb8;HEAD=0x4199d520;TAIL=0x4199d50c

def queue_state(track=0,velocity=100,due=0):
 m=attach(setup());m.map(D,80);m.map(Q,64*20+16);m.map(0x4199d508,0x70);m.map(0x41345ab0,4)
 m.write(HEAD,4,TAIL);m.write(TAIL,4,HEAD);m.write(0x431dc4bc,4,HEAD);m.write(0x431dc4c0,4,TAIL)
 for j in range(64):m.write(Q+j*20,4,Q+(j+1)*20 if j<63 else 0)
 m.write(0x431dc4c4,4,Q);m.write(D,1,0xec);m.write(D+1,1,0x10)
 m.write(D+16,1,60);m.write(D+17,1,velocity);m.write(D+18,2,(track<<12)|due)
 return m

for track,velocity in [(0,100),(0,0),(4,100),(9,100)]:
 m=queue_state(track,velocity);m.context=Snapshot(0,0,0);m.run(0x400efcb8,(D,0));q=queued(m)
 if track<=7:
  check('actual queue emits one valid-track item',len(q)==1)
  check('actual queue transfers context only for synth note-on',m.meta.candidate(key(q[0]['event']))==(m.context if track==0 and velocity else None))
 else:check('actual queue rejects track above seven',not q)
 check('queue candidate invalidated on actual reclamation',m.meta.candidate(key(Q)) is None)
 check('queue item preserves original allocation note',not q or q[0]['note']==60)
 cases.append({'name':'actual complete queue enqueue/emit/reclaim','track':track,'velocity':velocity,'steps':len(m.steps),'trace':m.observations})

m=queue_state(due=100);A=Snapshot(0,0,0);B=Snapshot(2,5,0);m.context=A;m.run(0x400efcb8,(D,0))
check('future queue item remains pending with original snapshot',not queued(m) and m.meta.candidate(key(Q))==A)
m.context=B;m.write(0x41345ab0,4,100);m.write(0x4199d508,4,0);m.run(0x400efcb8,(0,0));q=queued(m)
check('due conversion keeps enqueue snapshot after pattern change',len(q)==1 and m.meta.candidate(key(q[0]['event']))==A)
cases.append({'name':'actual delayed queue across supplied receiving-pattern change','steps':len(m.steps),'trace':m.observations})

m=queue_state();busy=[event(m) for _ in range(128)];m.context=A;m.run(0x400efcb8,(D,0))
check('actual queue event-allocation failure reclaims node without publication',not queued(m) and m.read(0x431dc4c4,4)==Q and m.meta.candidate(key(Q)) is None)
cases.append({'name':'actual queue event allocation failure','steps':len(m.steps),'trace':m.observations})
m=queue_state();m.write(0x431dc4c4,4,0);m.context=A;m.run(0x400efcb8,(D,0))
check('actual queue node exhaustion creates no context entry',not queued(m) and key(Q) not in m.meta.entries)
cases.append({'name':'actual queue node exhaustion','steps':len(m.steps),'trace':m.observations})

m=attach(setup());A=Snapshot(0,0,0)
for due in [50,10,50,100,30]:
 e=event(m);m.meta.initialize(key(e),A);m.run(0x400f07ac,(e,due))
node=m.read(0x4199fe94,4);timed=[];due_values=[]
while node:
 due_values.append(m.read(node+4,4));e=m.read(node+8,4)
 while e:
  timed.append(e);e=m.read(e+68,4)
 node=m.read(node+16,4)
check('actual timed scheduler keeps candidate on all five events',len(timed)==5 and all(m.meta.candidate(key(e))==A for e in timed))
check('actual timed scheduler preserves sorted due nodes',due_values==[10,30,50,100])
check('actual timed scheduler covers prepend, append and same-time event chain',all(pc in m.steps for pc in [0x400f0874,0x400f083a,0x400f085c]))
cases.append({'name':'actual timed publisher multiple ordering branches','steps':len(m.steps),'trace':m.observations})

# Model negative controls, not actual firmware ordering execution.
s=Sidecar();s.initialize(('events',0),A);s.accept(0,17,('events',0));s.copy(('events',1),('accepted',0))
check('corrected step-1 accepted-source adapter preserves scheduled context',s.candidate(('events',1))==A)
s.initialize(('events',0),B);s.copy(('events',1),('unknown',0))
check('unknown-copy source overwrites destination with fallback',s.candidate(('events',1)) is None)
result={'checks':checks,'passed':len(checks),'actual_cases':cases,'executed_steps':sum(c['steps'] for c in cases),'limits':['PC observer applies proposed metadata rules without injecting instructions','capture snapshots and accepted identities supplied','no hardware or concurrency execution','sequencer raw-copy helper executed with constructed cache, not complete sequencer producer','queue notes-only handler executed; other descriptor flags untested']}
pathlib.Path('outputs/Digitone-persistent-context-integration-execution.json').write_text(json.dumps(result,indent=2))
print('PASS',len(checks),'checks;',len(cases),'actual cases;',result['executed_steps'],'stock instructions')


