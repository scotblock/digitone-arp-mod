"""Read-only execution through stock mode entry and complete live Note On path."""
exec(open('work/execute-payload-lifecycle.py').read().split('checks=[];scenarios=[];total_steps=0')[0])
source=' def run'+pathlib.Path('work/execute-payload-lifecycle.py').read_text().split(' def run',1)[1].split('\nP=',1)[0]
source=source.replace('range(20000)','range(100000)')
source=source.replace("   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)","""   if pc==0x400dae08:
    size=self.read(self.reg['a7']+4,4)
    assert size==1, ('unexpected heap allocation',size)
    self.heap_calls.append(('allocate',size));self.reg['d0']=0x27008000;pc=self.get('(a7)+',4);continue
   if pc==0x400dae14:
    assert self.read(self.reg['a7']+4,4)==0x27008000
    self.heap_calls.append(('free',0x27008000));pc=self.get('(a7)+',4);continue
   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)""")
source=source.replace("   elif m=='st':self.put(ops[0],1,255)","""   elif m in ('st','seq','sne','sge','scc'):
    z=bool(self.sr&4);negative=bool(self.sr&8)^bool(self.sr&2)
    cond={'st':True,'seq':z,'sne':not z,'sge':not negative,'scc':not bool(self.sr&1)}[m]
    self.put(ops[0],1,255 if cond else 0)
   elif m=='link':
    self.put('-(a7)',4,self.reg[ops[0]]);self.reg[ops[0]]=self.reg['a7'];disp=self.get(ops[1],2);disp=disp-65536 if disp&32768 else disp;self.reg['a7']=(self.reg['a7']+disp)&0xffffffff
   elif m=='unlk':
    self.reg['a7']=self.reg[ops[0]];self.reg[ops[0]]=self.get('(a7)+',4)
   elif m=='ext':
    width=1 if n==2 else 2;x=self.get(ops[0],width);x=x-(1<<(8*width)) if x&(1<<(8*width-1)) else x;self.put(ops[0],n,x);self.flags(x,n)
   elif m=='mulu':
    x=self.get(ops[0],n);y=self.get(ops[1],n);self.put(ops[1],4,x*y);self.flags(x*y,4)
   elif m=='divs':
    x=self.get(ops[0],4);y=self.get(ops[1],4);x=x-0x100000000 if x&0x80000000 else x;y=y-0x100000000 if y&0x80000000 else y
    assert x!=0;q=abs(y)//abs(x);q=-q if (x<0)!=(y<0) else q;assert -0x80000000<=q<=0x7fffffff
    self.put(ops[1],4,q);self.flags(q,4)""")
exec('if True:\n'+source);Machine.run=run
oldread=Machine.read
def read_rom(self,a,n):
 if all(a+j in self.mem for j in range(n)):return oldread(self,a,n)
 if base<=a and a+n<=base+len(b) and all(a+j not in self.mem for j in range(n)):return int.from_bytes(b[a-base:a-base+n],'big')
 return oldread(self,a,n)
Machine.read=read_rom
RANGES.extend([(0x400ec284,0x400ec2f0),(0x400dc406,0x400dc90c),(0x400e0eb8,0x400e0fe2),(0x400e114a,0x400e11bc),(0x40093b72,0x40093f7a),(0x4009e39e,0x4009e3cc),(0x40106c30,0x40106d46),(0x40095d98,0x40095ee8),(0x40126618,0x40126624),(0x400db642,0x400db68a),(0x40001cda,0x40001d28),(0x40001632,0x40001696),(0x400ef810,0x400efc4e),(0x4009c2f8,0x4009c314),(0x400f04c0,0x400f0504),(0x400f06d4,0x400f06f2),(0x400f0886,0x400f08f0),(0x400d5eca,0x400d5ee6),(0x400d5880,0x400d58d2),(0x4012fc1e,0x4012fcba),(0x400ababe,0x400abaf4),(0x400d653a,0x400d65de),(0x400d6944,0x400d6950),(0x400d6d46,0x400d6db6),(0x400d6aba,0x400d6ade),(0x400d75fe,0x400d760a),(0x4015a3ae,0x4015a40a),(0x4012c2fe,0x4012c33a),(0x400ae4b0,0x400ae502),(0x400ae458,0x400ae45e),(0x400d95cc,0x400d95ee),(0x400012c8,0x400012e2)])
K=0x431d1758;PAT=0x407b00cc;PAGE=0x27000038;V=0x27001000;N=0x26000000;REG=0x26100000;NOTIFY=0x26200000;MSG=0x29000000
checks=[];cases=[]
def check(n,c):assert c,n;checks.append(n)
def state(gate=1,assigned=True,step=-1):
 m=fresh();m.heap_calls=[]
 for a,n in [(0x28400000,0x200),(0x28500000,0x40),(0x419a257c,4),(0x24000000,0x1000),(0x28000000,0x100),(0x27000000,0x8100),(K,4*0x2a18),(PAT,0x1611d),(0x41342150,4),(0x4131b990,0xc0),(0x41945ed4,4),(0x41945f50,0x1000),(0x41946f50,0x2000),(0x41962000,0xd0),(0x4195e004,4),(REG,16*16),(0x4199fe94,4),(N,64*20),(0x419a2fd0,0x60),(0x80004614,4),(0x80003f54,4),(NOTIFY,0x200),(0x401feafc,12),(0x400002b8,4),(0x400002fc,4),(0xfc04c01c,2),(0xfc04c07f,1),(MSG,32),(0x412b8f4c,0x988)]:m.map(a,n)
 m.write(PAGE+0x16,1,1);m.write(PAGE+0x18,1,1);m.write(PAGE,4,0x401a3ba8);m.write(PAGE+0x34,4,V);m.write(PAGE+0x38,4,V+32);m.write(PAGE+0x3c,4,V+32)
 m.write(V,4,0x27002000);m.write(V+8,4,0x400d5880);m.write(V+12,4,0x400d5eca);m.write(V+16,4,0x27002010);m.write(V+24,4,0x400ae4b0);m.write(V+28,4,0x400ae458)
 m.write(0x419a257c,4,0x28400000);m.write(0x28400198,4,0x28500000);m.write(0x2840019c,4,0x28500000);m.write(0x284001a0,4,0x28500040)
 m.write(0x4131ba40,4,gate);m.write(0x4131ba1c,4,3);m.write(0x4131b9e4,4,15);m.write(0x4131ba10,4,0xffffffff)
 for j in range(8):m.write(0x4131b9e8+j*4,4,0 if assigned and j==0 else 0xffffffff)
 for j in range(128):m.write(0x41946f70+j*4,4,0xffffffff)
 m.write(0x80003f54,4,0x24000000);m.write(0x41342150,4,PAT);m.write(PAT+0x16119,4,0);m.write(0x401feafc,4,step)
 # Zero chord offset takes the stock single-note path; unused local notes are ROM -1s.
 m.write(PAT+0x3cd,1,0);m.write(PAT+0x3ce,1,255)
 m.write(0x4195e004,4,REG)
 for j in range(16):m.write(REG+j*16+8,4,REG+(j+1)*16 if j<15 else 0)
 for j in range(64):m.write(N+j*20+16,4,N+(j+1)*20 if j<63 else 0)
 m.write(0x4199fe9c,4,N)
 for j in range(4):m.write(K+j*0x2a18+0x2a14,1,255)
 for j in range(8):m.write(0x419a2fd0+0x18+j*4,4,PAT);m.write(0x419a2fd0+0x38+j*4,4,PAT)
 m.write(0x401feb04,4,NOTIFY);m.write(NOTIFY+0x10,4,15);m.write(NOTIFY+0x14,4,NOTIFY+0x40)
 for j,x in enumerate([0x90,60,100]):m.write(MSG+j,1,x)
 return m
# Complete actual virtual entry: vtable +18 -> +14 thunk -> base dispatcher -> callback.
for gate,assigned,step in [(0,True,-1),(1,False,-1),(1,True,-1),(1,True,0)]:
 m=state(gate,assigned,step);m.run(0x400d6944,(PAGE,0x28000000));entry_steps=list(m.steps)
 check(f'{gate}/{assigned}/{step}: complete virtual entry returns',0x400d65d4 in entry_steps and 0x400d6d46 in entry_steps and 0x400ae458 in entry_steps)
 check(f'{gate}/{assigned}/{step}: real thunk subtracts 0x38',m.read(PAGE+0x2c,4)==0x28000000)
 check(f'{gate}/{assigned}/{step}: both constructor callbacks executed in order',entry_steps.index(0x400d5eca)<entry_steps.index(0x400ae458))
 check(f'{gate}/{assigned}/{step}: note gate preserved by entry',m.read(0x4131ba40,4)==gate)
 start=len(m.steps)
 try:m.run(0x400dc8c4,(MSG,3,8))
 except Exception:
  print('LAST', [hex(x) for x in m.steps[-8:]],m.reg);raise
 path=m.steps[start:]
 check(f'{gate}/{assigned}/{step}: full handler restores stack and mask',m.reg['a7']==0x30002000 and m.sr&0xff00==0x2000)
 check(f'{gate}/{assigned}/{step}: publication matches gates',bool(m.read(0x4199fe94,4))==bool(gate and assigned))
 check(f'{gate}/{assigned}/{step}: input notification matches accepted route',m.read(NOTIFY+4,4)==int(bool(gate and assigned)))
 if gate and assigned:
  e=m.read(m.read(0x4199fe94,4)+8,4)
  check(f'{step}: real published note and track',m.read(e+24,1)==60 and m.read(e+8,4)==0 and m.read(e+4,4)==1)
  check(f'{step}: real payload attachment follows step eligibility',m.read(e+56,4)==(P if step==0 else 0))
  if step==0:check('actual parameter producer populates 79 entries',m.read(P,4)==1 and m.read(P+8,4)==79 and all(m.read(P+20+8*j,2)==j for j in range(79)))
 cases.append({'gate':gate,'assigned':assigned,'step':step,'entry_steps':[hex(x) for x in entry_steps],'handler_steps':[hex(x) for x in path],'queue_head':hex(m.read(0x4199fe94,4)),'notification_count':m.read(NOTIFY+4,4),'payload_ref':m.read(P,4),'heap_boundary_calls':m.heap_calls})
 print('CASE',gate,assigned,step,len(path))
pathlib.Path('outputs/Digitone-full-handler-transition-execution-results.json').write_text(json.dumps({'checks':checks,'cases':cases,'firmware_modified':False},indent=2))








