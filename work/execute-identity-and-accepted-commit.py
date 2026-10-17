"""Execute stock arp setup and retained-copy caller; PC-only commit observer."""
exec(open('work/execute-full-handler-transition.py').read().split('# Complete actual virtual entry')[0])
RANGES.extend([(0x40097014,0x4009750a),(0x4009dd80,0x4009de66),(0x4009df06,0x4009df0a),(0x4009f266,0x4009f290)])
# Record observer before every executed instruction; unchanged decoded bytes.
source=source.replace('   self.steps.append(pc)','   self.steps.append(pc)\n   if hasattr(self,"observe"):self.observe(pc)')
exec('if True:\n'+source);Machine.run=run
route_source=source.replace('def run(self,entry,args=()):','def route(self,entry,stop):')
route_source=route_source.replace("  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry","  pc=entry")
route_source=route_source.replace('if pc==0xffffffff:break','if pc==stop:break')
route_source=route_source.replace('  self.reg[\'a7\']+=len(args)*4','')
route_source=route_source.replace('  assert all(self.reg[r]==v for r,v in saved.items())','')
route_source=route_source.replace('  assert self.reg["a7"]==initial_sp','').replace("  assert self.reg['a7']==initial_sp",'')
exec('if True:\n'+route_source);Machine.route=route
SET=0x24000000;NOTES=0x25000000;OUT=NOTES+0x100;STATE=0x41344530;RETAINED=0x41345f08;EV=0x21000000;NODE=0x26000000
checks=[];cases=[]
def check(n,c):assert c,n;checks.append(n)
def create():
 m=fresh();m.heap_calls=[]
 for a,n in [(0x413424ec,0x4000),(SET,0x400),(NOTES,0x200),(0x800034c4,0x3000),(0x41346600,0x100),(NODE,64*20),(0x4199fe94,4)]:m.map(a,n)
 m.write(SET+0x10f,1,1)
 return m

def setup_call(m,note=60,priority=2,settings=SET,count=1,track=0):
 m.write(NOTES,1,note);m.write(OUT,4,0);m.write(OUT+4,4,0)
 return m.run(0x4009719e,(track,count,NOTES,0,0,priority,settings,OUT,OUT+4))

for initial,want in [(0,1),(1,2),(0xfffffffe,0xffffffff),(0xffffffff,1)]:
 m=create();m.write(STATE+24,4,initial);start=len(m.steps);ret=setup_call(m)
 check('actual new setup increments identity and skips zero',ret==want and m.read(STATE+24,4)==want)
 check('actual new setup enables arp and creates active list',m.read(OUT,4)==1 and m.read(0x41345620,4)!=0)
 cases.append({'name':'actual new identity','initial':hex(initial),'returned':hex(ret),'steps':len(m.steps)-start,'visited':[hex(x) for x in sorted(set(m.steps[start:]))]})

m=create();first=setup_call(m);st=bytes(m.mem[STATE+i] for i in range(40));start=len(m.steps);ret=setup_call(m,64)
check('actual additive setup returns zero without changing identity',ret==0 and m.read(STATE+24,4)==first)
check('actual additive setup preserves priority/settings',m.read(STATE+32,4)==SET and m.read(STATE+36,4)==2)
check('actual additive setup expands bitmap',m.read(0x413445d0+4,4)&(1<<28) and m.read(0x413445d0+8,4)&1)
cases.append({'name':'actual additive','returned':ret,'steps':len(m.steps)-start})
start=len(m.steps);ret=setup_call(m,67,1)
check('actual lower priority rejected without identity replacement',ret==0 and m.read(STATE+24,4)==first)
check('actual rejected note absent from bitmap',m.read(0x413445d0+8,4)&(1<<3)==0)
cases.append({'name':'actual rejected','steps':len(m.steps)-start})
m.write(SET+0x200+0x10f,1,1);start=len(m.steps);ret=setup_call(m,67,2,SET+0x200)
check('actual settings replacement creates next identity',ret==2 and m.read(STATE+32,4)==SET+0x200)
check('actual settings replacement clears prior notes',m.read(0x413445d0+4,4)==0 and m.read(0x413445d0+8,4)==8)
cases.append({'name':'actual settings replacement','steps':len(m.steps)-start})
start=len(m.steps);m.run(0x4009713c)
check('actual ordinary reset preserves identity counter',m.read(STATE+24,4)==2)
check('actual ordinary reset clears active list',m.read(0x41345620,4)==0)
ret=setup_call(m,60)
check('actual post-reset identity advances rather than repeats one',ret==3)
cases.append({'name':'actual reset and restart','steps':len(m.steps)-start})

m=create();start=len(m.steps)
for track in range(4):
 ret=setup_call(m,track=track)
 check('actual counters are per-track and legitimately coincide',ret==1 and m.read(STATE+track*40+24,4)==1)
m.run(0x4009713c)
check('actual all-track reset preserves all counters',all(m.read(STATE+t*40+24,4)==1 for t in range(4)))
cases.append({'name':'four-track independent identities and reset','steps':len(m.steps)-start})

# Call actual setup from its pitch caller, then follow the real branch to retained copy.
for kind in ['new','additive','rejected','replace','off']:
 m=create();old_context=0x80000080;new_context=0x80000082
 if kind in ('additive','rejected','replace'):setup_call(m)
 if kind=='off':m.write(SET+0x10f,1,0)
 settings=SET
 if kind=='replace':settings=SET+0x200;m.write(settings+0x10f,1,1)
 e=event(m);m.write(e+4,4,1);m.write(e+8,4,0);m.write(e+12,4,1 if kind=='rejected' else 2);m.write(e+20,4,1);m.write(e+24,1,64);m.write(e+40,4,0);m.write(e+52,4,0)
 # Meaningful preceding retained snapshot for additive/rejected cases.
 m.write(RETAINED+64,4,m.read(STATE+24,4))
 m.reg['a6']=0x30001800;m.reg['a3']=e;m.reg['a4']=NODE;m.reg['a5']=settings;m.reg['a2']=0x800034c4
 old_identity=m.read(STATE+24,4);metadata={'identity':old_identity,'word':old_context,'busy':False};reads=[]
 def observe(pc):
  if pc==0x4009719e:metadata['busy']=True
  # Simulate reader opportunity at every stock instruction while constructing.
  visible=None if metadata['busy'] or metadata['identity']!=m.read(STATE+24,4) else metadata['word']
  reads.append((pc,visible))
 m.observe=observe;start=len(m.steps);m.route(0x4009dd80,0x4009ddb0);ret=m.reg['d0']
 if ret:
  m.route(0x4009ddb0,0x4009de46)
  check('real accepted caller copies event identity into retained template',m.read(RETAINED+64,4)==ret and m.read(e+64,4)==ret and 0x400f0690 in m.steps[start:])
  # Proposed bounded commit, after stock byte copy; no instruction patch executed.
  metadata.update(identity=ret,word=new_context,busy=False)
  # At this mid-function boundary the two common-copy arguments remain pushed.
  check('accepted boundary has exactly two pending copy arguments',m.reg['a7']==0x30002000-8)
  outcome='commit'
 else:
  m.route(0x4009ddb0,0x4009df0a)
  check('real additive/rejected/off caller does not copy retained template',0x400f0690 not in m.steps[start:])
  metadata['busy']=False;outcome='preserve'
 first_guard=next(i for i,(pc,v) in enumerate(reads) if pc==0x4009719e)
 check('interleaved reader never sees partially constructed accepted context',all(v is None for pc,v in reads[first_guard:]))
 if ret:
  # Separate proposed commit-store interleavings: busy remains asserted until last store.
  record={'identity':old_identity,'word':old_context,'binding':0,'busy':True}
  for field,value in [('identity',ret),('word',new_context),('binding',0)]:
   record[field]=value
   check('reader declines each intermediate commit store',record['busy'])
  record['busy']=False
  check('reader sees complete tuple after final valid publication',record['identity']==ret and record['word']==new_context and not record['busy'])
 check('proposed commit outcome matches actual return and branch',metadata['word']==(new_context if ret else old_context))
 check('caller preserves modeled stack and SR',m.reg['a7']==0x30002000-(8 if ret else 0) and m.sr&0xff00==0x2000)
 cases.append({'name':'actual setup through retained-copy caller','kind':kind,'return':ret,'outcome':outcome,'steps':len(m.steps)-start,'retained_identity':m.read(RETAINED+64,4),'metadata':metadata,'reader_opportunities':len(reads),'limitation':'Python busy/commit observer, not injected instructions; empty voice-stop mask supplied'})

result={'passed':len(checks),'checks':checks,'cases':cases,'stock_steps':sum(c['steps'] for c in cases),'firmware_modified':False,'limits':['Controlled synth track zero; mode one; single-note, no duration timer','Voice-stop mask zero, no producer/scheduler concurrency','Busy gate and context commit are hypothetical Python operations','No inserted-hook register/stack or exception validation','Whole-image indirect identity writers not excluded']}
pathlib.Path('outputs/Digitone-actual-identity-and-accepted-commit-results.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'checks',len(cases),'cases',result['stock_steps'],'stock steps')
