"""Read-only bounded execution of the complete disabled-arp note route."""
exec(open('work/execute-cache-ordering.py').read().split('checks=[];cases=[]')[0])
source=' def run'+pathlib.Path('work/execute-payload-lifecycle.py').read_text().split(' def run',1)[1].split('\nP=',1)[0]
source=source.replace('def run(self,entry,args=()):','def route(self,entry,stop):')
source=source.replace("  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry","  pc=entry")
source=source.replace('if pc==0xffffffff:break','if pc==stop:break')
source=source.replace("  self.reg['a7']+=len(args)*4",'')
source=source.replace("  assert all(self.reg[r]==v for r,v in saved.items())",'')
exec('if True:\n'+source)
Machine.route=route
RANGES.extend([(0x4009dc5e,0x4009e352),(0x4009e70c,0x4009f074),(0x4009f0ea,0x4009f266),(0x4009719e,0x4009755e)])
checks=[];cases=[]
def check(name,value):assert value,name;checks.append(name)
def initialize(m):
 for a,n in [(0x41346600,0x100),(0x800034c4,0x3000),(0x413463b0,512),(0x27000000,64),(0x41344540,0x40*4),(0x41345620,16),(0x41345f08,4*72)]:m.map(a,n)
 m.reg['a6']=0x30001800;m.reg['a2']=0x27000000
 # All voices initially idle, DSP state synchronization clean.
 m.write(0x41346644,4,0)

def consume_route(m):
 q=queued(m);node=m.read(0x4199fe94,4);retired=[]
 while node:
  m.reg['a4']=node;e=m.read(node+8,4)
  while e:
   m.reg['a3']=e;m.reg['d2']=m.read(e+8,4)
   p=m.read(e+56,4);before=m.read(p,4) if p else None;begin=len(m.steps);wb=len(m.writes)
   try:m.route(0x4009dc5e,0x4009cef0)
   except Exception:
    print('last route PCs', [hex(x) for x in m.steps[-15:]])
    raise
   check('event address preserved at common completion',m.reg['a3']==e)
   check('payload pointer preserved before retirement',m.read(e+56,4)==p)
   check('payload count unchanged by disabled-arp route',not p or m.read(p,4)==before)
   check('template capture absent from disabled-arp route',0x400f0690 not in m.steps[begin:])
   owned=[{'address':hex(a),'length':n,'value':v} for a,n,v in m.writes[wb:] if p and p<=a<p+0x504]
   check('no writes into payload record during route',not owned)
   trace=[hex(x) for x in m.steps[begin:]]
   nxt=m.read(e+68,4);m.run(0x400f065c,(e,))
   retired.append({'event':hex(e),'onoff':m.read(e+4,4),'note':m.read(e+24,1),'payload':hex(p),'count_before':before,'count_after':m.read(p,4) if p else None,'route_steps':len(trace),'route_addresses':trace})
   e=nxt
  nxt=m.read(node+16,4);m.run(0x400f04f8,(nxt,));m.run(0x400f06d4,(node,));node=nxt
 return retired
for mode in [2,3]:
 for selector,a,bnote in [(0,60,64),(1,64,60),(2,60,64)]:
  m=setup(mode,selector);initialize(m)
  p=pop(m,a);emit(m,a,True,p);first=consume_route(m)
  bp=pop(m,bnote);emit(m,bnote,True,bp);second=consume_route(m)
  emit(m,bnote,False);last=consume_route(m)
  check('actual complete disabled route still permits replay underflow',m.read(p,4)==0xffffffff)
  cases.append({'mode':mode,'selector':selector,'events':first+second+last,'steps':len(m.steps)})
m=setup();initialize(m);p=pop(m,60);emit(m,60,True,p);bp=pop(m,64);emit(m,64,True,bp);emit(m,64,False)
last=consume_route(m);check('deferred route still underflows A',m.read(p,4)==0xffffffff)
cases.append({'name':'deferred entire producer burst','events':last,'steps':len(m.steps)})
RANGES.extend([(0x4009b600,0x4009b69e),(0x4009bd8a,0x4009bde8)])
leaf_cases=[]
for voice in range(8):
 m=setup();initialize(m);m.map(0x431a3ed4,8*12)
 p=pop(m,60);m.write(p+8,4,2)
 for offset,index,value in [(20,0,123),(28,78,456)]:
  m.write(p+offset,2,index);m.write(p+offset+2,2,value)
 before=bytes(m.mem[p+i] for i in range(0x504));begin=len(m.steps)
 m.run(0x4009b600,(voice,p,0x800034c4))
 check('parameter apply leaves entire payload record unchanged',before==bytes(m.mem[p+i] for i in range(0x504)))
 check('parameter apply writes expected first and last voice parameters',all(m.read(0x800034c4+2*(voice*79+index+8)+2,2)==value for index,value in [(0,123),(78,456)]))
 leaf_cases.append({'name':'parameter playback','voice':voice,'steps':len(m.steps)-begin,'unchanged_payload':True})
for available in [True,False]:
 m=setup();initialize(m);p=pop(m,60);e=event(m,p)
 if not available:m.write(0x4199fea0,4,0)
 before=m.read(p,4);begin=len(m.steps);m.run(0x4009bd8a,(e,3));child=m.read(e+68,4)
 check('child clone never retains or releases original payload',m.read(p,4)==before)
 check('child clone has null payload or allocation failed',bool(child)==available and (not child or m.read(child+56,4)==0))
 leaf_cases.append({'name':'voice child clone','event_available':available,'child':hex(child),'steps':len(m.steps)-begin,'payload_count':m.read(p,4)})
pathlib.Path('outputs/Digitone-disabled-arp-consumer-execution-results.json').write_text(json.dumps({'firmware_modified':False,'checks':checks,'cases':cases,'leaf_cases':leaf_cases,'sha256_section3':hashlib.sha256(b).hexdigest(),'limitations':['Controlled initially idle voices; state synchronization flag zero.','Entry at recovered type-zero note route, stop before common retirement; retirement helper executed separately.','No interrupt prologue/epilogue, task scheduler, upstream UI or hardware emulation.','Bounded custom interpreter is not independently hardware validated.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'leaf_cases':len(leaf_cases),'steps':sum(c['steps'] for c in cases)+sum(c['steps'] for c in leaf_cases)}))
