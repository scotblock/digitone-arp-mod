"""Bounded execution of stock ColdFire helpers; no firmware modification."""
exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
import json,hashlib
RANGES=[(0x400f05d6,0x400f06d4),(0x400ec23c,0x400ec282)]
class Machine:
 def __init__(self):
  self.reg={f'{k}{i}':0 for k in ['d','a'] for i in range(8)};self.reg['a7']=0x30002000;self.sr=0x2000;self.mem={};self.steps=[];self.writes=[]
 def map(self,a,n):self.mem.update({a+i:0 for i in range(n)})
 def read(self,a,n):
  if any(a+i not in self.mem for i in range(n)):raise RuntimeError(f'unmapped read {a:08x}/{n}')
  return int.from_bytes(bytes(self.mem[a+i] for i in range(n)),'big')
 def write(self,a,n,v):
  if any(a+i not in self.mem for i in range(n)):raise RuntimeError(f'unmapped write {a:08x}/{n}')
  for i,x in enumerate((v&((1<<(8*n))-1)).to_bytes(n,'big')):self.mem[a+i]=x
  self.writes.append((a,n,v&((1<<(8*n))-1)))
 def ea(self,s,n=4):
  if s in self.reg:return self.reg[s]
  idx=re.fullmatch(r'(-?\$[0-9a-f]+)\((a[0-7]), ([da][0-7])\.l(?: \* ([1248]))?\)',s)
  if idx:return (int(idx[1].replace('$',''),16)+self.reg[idx[2]]+self.reg[idx[3]]*int(idx[4] or 1))&0xffffffff
  m=re.fullmatch(r'(-?\$[0-9a-f]+)?\((a[0-7])\)(\+)?',s)
  if m:return (self.reg[m[2]]+(int(m[1].replace('$',''),16) if m[1] else 0))&0xffffffff
  if s.startswith('$'):
   v=int(re.findall(r'\$([0-9a-f]+)',s)[0],16)
   if s.endswith('.w') and v&0x8000:v|=0xffff0000
   return v
  raise RuntimeError(('unsupported EA',s))
 def get(self,s,n):
  if s=='sr':return self.sr
  if s in self.reg:return self.reg[s]&((1<<(8*n))-1)
  if s.startswith('#$'):return int(s[2:],16)&((1<<(8*n))-1)
  if s.startswith('-('):
   r=s[2:4];self.reg[r]-=n
   return self.read(self.reg[r],n)
  a=self.ea(s,n);v=self.read(a,n)
  if s.endswith(')+'):
   r=re.search(r'\((a[0-7])\)',s)[1];self.reg[r]+=n
  return v
 def put(self,s,n,v):
  mask=(1<<(8*n))-1;v&=mask
  if s=='sr':self.sr=v;return
  if s in self.reg:self.reg[s]=(self.reg[s]&~mask)|v;return
  if s.startswith('-('):
   r=s[2:4];self.reg[r]-=n;self.write(self.reg[r],n,v);return
  self.write(self.ea(s,n),n,v)
  if s.endswith(')+'):
   r=re.search(r'\((a[0-7])\)',s)[1];self.reg[r]+=n
 def flags(self,v,n,overflow=False,carry=False,extend=False):
  mask=(1<<(8*n))-1;v&=mask
  self.sr=(self.sr&~15)|(8 if v&(1<<(8*n-1)) else 0)|(4 if v==0 else 0)|(2 if overflow else 0)|(1 if carry else 0)
  if extend:self.sr=(self.sr&~16)|(16 if carry else 0)
 def run(self,entry,args=()):
  initial_sp=self.reg['a7'];saved={r:self.reg[r] for r in ['d2','d3','d4','d5','d6','d7','a2','a3','a4','a5']};saved_sr=self.sr&0xff00
  for v in reversed(args):self.put('-(a7)',4,v)
  self.put('-(a7)',4,0xffffffff);pc=entry
  for _ in range(20000):
   if pc==0xffffffff:break
   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)
   i=next(md.disasm(b[pc-base:pc-base+16],pc,count=1));m=i.mnemonic.split('.')[0];n={'b':1,'w':2,'l':4}.get(i.mnemonic.split('.')[-1],4);ops=re.split(r', (?![^()]*\))',i.op_str);nextpc=pc+i.size
   self.steps.append(pc)
   if i.id==0:
    assert bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)]
    self.flags(self.reg[f'a{(int.from_bytes(i.bytes,"big")&7)}'],4)
   elif m in ('move','movea','moveq'):
    v=self.get(ops[0],n)
    if m=='moveq' and v&128:v|=0xffffff00
    if m=='movea' and n==2 and v&0x8000:v|=0xffff0000
    self.put(ops[1],4 if m in ('movea','moveq') else n,v)
    if m in ('move','moveq') and 'sr' not in ops:self.flags(v,n)
   elif m=='swap':
    v=self.get(ops[0],4);v=((v<<16)|(v>>16))&0xffffffff;self.put(ops[0],4,v);self.flags(v,4)
   elif m=='btst':
    bit=self.get(ops[0],4)%(32 if ops[1] in self.reg else 8);v=self.get(ops[1],4 if ops[1] in self.reg else 1);self.sr=(self.sr&~4)|(0 if v&(1<<bit) else 4)
   elif m=='lea':self.put(ops[1],4,self.ea(ops[0]))
   elif m=='pea':self.put('-(a7)',4,self.ea(ops[0]))
   elif m=='clr':self.put(ops[0],n,0);self.flags(0,n)
   elif m=='tst':self.flags(self.get(ops[0],n),n)
   elif m in ('cmp','cmpa','cmpi'):
    x=self.get(ops[0],n);y=self.get(ops[1],n);v=y-x;sign=1<<(n*8-1)
    self.flags(v,n,bool((y^x)&(y^v)&sign),y<x)
   elif m in ('and','andi','or','ori','eor','eori'):
    x=self.get(ops[0],n);y=self.get(ops[1],n);v=x&y if m.startswith('and') else x|y if m.startswith('or') else x^y
    self.put(ops[1],n,v);self.flags(v,n)
   elif m in ('not','neg'):
    x=self.get(ops[0],n);v=~x if m=='not' else -x;self.put(ops[0],n,v);self.flags(v,n)
   elif m in ('lsl','lsr','asr'):
    count=self.get(ops[0],4)&63;x=self.get(ops[1],n);bits=n*8
    if m=='asr':x=x-(1<<bits) if x&(1<<(bits-1)) else x
    v=x<<count if m=='lsl' else x>>count
    self.put(ops[1],n,v);self.flags(v,n)
   elif m=='muls':
    x=self.get(ops[0],4);y=self.get(ops[1],4);x=x-0x100000000 if x&0x80000000 else x;y=y-0x100000000 if y&0x80000000 else y
    self.put(ops[1],4,x*y);self.flags(x*y,4)
   elif m=='ff1':
    x=self.get(ops[0],4);self.put(ops[0],4,32-x.bit_length())
   elif m=='st':self.put(ops[0],1,255)
   elif m in ('mvs','mvz'):
    x=self.get(ops[0],n)
    if m=='mvs' and x&(1<<(8*n-1)):x-=1<<(8*n)
    self.put(ops[1],4,x);self.flags(x,4)
   elif m in ('add','sub','addq','subq','adda','suba','addi','subi'):
    x=self.get(ops[0],n);y=self.get(ops[1],n);sub=m.startswith('sub');v=y-x if sub else y+x;mask=(1<<(n*8))-1;sign=1<<(n*8-1)
    self.put(ops[1],n,v)
    if not m.endswith('a') and not ops[1].startswith('a'):
     overflow=bool(((y^x)&(y^v)&sign) if sub else ((~(y^x))&(y^v)&sign))
     self.flags(v,n,overflow,(y<x) if sub else (v>mask),True)
   elif m=='movem':
    storing=bool(re.match(r'^[da][0-7](?:-|/|$)',ops[0]));regs=ops[0] if storing else ops[1];names=[]
    for group in regs.split('/'):
     if '-' in group:
      lo,hi=group.split('-');names.extend(f'{lo[0]}{k}' for k in range(int(lo[1]),int(hi[1])+1))
     else:names.append(group)
    if storing:
     a=self.ea(ops[1])
     for k,r in enumerate(names):self.write(a+4*k,4,self.reg[r])
    else:
     a=self.ea(ops[0])
     for k,r in enumerate(names):self.reg[r]=self.read(a+4*k,4)
   elif m in ('bra','beq','bne','bge','ble','bgt','bcs','bcc','bpl','bmi','blt'):
    z=bool(self.sr&4);negative=bool(self.sr&8)^bool(self.sr&2)
    take={'bra':True,'beq':z,'bne':not z,'bge':not negative,'ble':z or negative,'bgt':not z and not negative,'bcs':bool(self.sr&1),'bcc':not bool(self.sr&1),'bpl':not bool(self.sr&8),'bmi':bool(self.sr&8),'blt':negative}[m]
    if take:nextpc=int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16)
   elif m=='jsr':self.put('-(a7)',4,nextpc);nextpc=self.ea(ops[0])
   elif m=='jmp':nextpc=self.ea(ops[0])
   elif m=='rts':nextpc=self.get('(a7)+',4)
   else:raise RuntimeError((hex(pc),i.mnemonic,i.op_str))
   pc=nextpc
  else:raise RuntimeError('instruction budget exceeded')
  self.reg['a7']+=len(args)*4
  assert self.reg['a7']==initial_sp
  assert all(self.reg[r]==v for r,v in saved.items())
  assert self.sr&0xff00==saved_sr
  return self.reg['d0']

P=0x20000000;E=0x21000000;C=0x22000000;T=0x23000000;TRAILER=b'OWNED-TRAILER-16'
def fresh():
 m=Machine()
 for a,n in [(P,0x14110),(E,128*72),(C,128*72),(T,5*72),(0x4199fe98,12),(0x30000000,0x3000)]:m.map(a,n)
 for s in range(64):m.write(P+s*0x504+16,4,P+(s+1)*0x504 if s<63 else 0)
 m.write(0x4199fe98,4,P)
 for s in range(128):m.write(E+s*72+68,4,E+(s+1)*72 if s<127 else 0)
 m.write(0x4199fea0,4,E)
 for i,x in enumerate(TRAILER):m.write(P+0x14100+i,1,x)
 return m
def pop(m,tag=0):
 p=m.run(0x400f05d6);m.write(p+8,4,1);m.write(p+20,4,tag);return p
def event(m,p=0):
 e=m.run(0x400f0626)
 if e:m.write(e+56,4,p)
 return e
def cache(m,n,p):m.write(C+n*72+56,4,p);return C+n*72
def raw(m,n):
 e=m.run(0x400f0626)
 if e:m.run(0x400ec23c,(e,C+n*72,72))
 return e
def freechain(m):
 p=m.read(0x4199fe98,4);seen=[]
 while p:
  if p in seen:return {'slots':seen,'cycle_at':p}
  assert P<=p<P+0x14100 and (p-P)%0x504==0
  seen.append(p);p=m.read(p+16,4)
 return {'slots':seen,'cycle_at':None}
checks=[];scenarios=[];total_steps=0
def check(n,c):assert c,n;checks.append(n)
def save(name,m,details):
 global total_steps
 check(name+': trailer unchanged',bytes(m.mem[P+0x14100+i] for i in range(16))==TRAILER)
 total_steps+=len(m.steps)
 scenarios.append({'name':name,'details':details,'executed_instructions':len(m.steps),'visited_instruction_addresses':[hex(x) for x in sorted(set(m.steps))],'record_headers':[{'slot':s,'ref':m.read(P+s*0x504,4),'next':hex(m.read(P+s*0x504+16,4))} for s in range(64) if m.read(P+s*0x504,4)!=0], 'free_chain':{'count':len(freechain(m)['slots']),'cycle_at':freechain(m)['cycle_at']}})

# Validate the used copy semantics against independent byte-array outcomes,
# including the stock routine's 16-byte, 4-byte and byte-tail loops.
for length in [0,1,3,4,7,15,16,17,31,32,71,72,79]:
 m=fresh();src=C;dest=C+0x100
 pattern=bytes((k*37+11)&255 for k in range(80))
 for k,x in enumerate(pattern):m.write(src+k,1,x)
 for k in range(84):m.write(dest-2+k,1,0xa5)
 for k in range(2,6):m.reg[f'd{k}']=0x13572468+k
 m.run(0x400ec23c,(dest,src,length))
 check(f'actual memcpy length {length} matches bytes and preserves guards/source',bytes(m.mem[dest+k] for k in range(length))==pattern[:length] and all(m.mem[dest+k]==0xa5 for k in [-2,-1,length,length+1]) and bytes(m.mem[src+k] for k in range(80))==pattern and m.reg['d0']==dest)

# Nonzero saved registers and nondefault interrupt mask exercise restoration
# rather than relying only on zero-initialized register state.
m=fresh();m.sr=0x2400
for k in range(2,6):m.reg[f'd{k}']=0x24681357+k
for k in [2,3]:m.reg[f'a{k}']=0x33330000+k
p=pop(m,42);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f065c,(e,));m.run(0x400f0690,(T,T+4*72))
check('helper sequence restores nonzero preserved registers and interrupt mask',(m.sr&0xff00)==0x2400 and all(m.reg[f'd{k}']==0x24681357+k for k in range(2,6)) and all(m.reg[f'a{k}']==0x33330000+k for k in [2,3]))

m=fresh();rs=[pop(m,s) for s in range(64)]
check('64 distinct pops and empty free head',len(set(rs))==64 and m.read(0x4199fe98,4)==0)
try:m.run(0x400f05d6);raise AssertionError('null payload pop unexpectedly succeeded')
except RuntimeError as exc:check('65th pop faults at null+16 rather than returning trailer','00000010/4' in str(exc))
# The fault leaves an execution frame: use a fresh machine for subsequent scenarios.
m=fresh();rs=[pop(m,s) for s in range(64)]
for p in rs:m.run(0x400f05f8,(p,))
check('release is LIFO and restores all 64 records',freechain(m)['slots']==list(reversed(rs)))
save('valid 64-record allocation/release',m,{})

m=fresh();p=pop(m,60);cache(m,60,p);e=raw(m,60);m.run(0x400f065c,(e,))
check('completion leaves borrowed cache pointer to zero-ref free record',m.read(C+60*72+56,4)==p and m.read(p,4)==0 and p in freechain(m)['slots'])
replay=raw(m,60);m.run(0x400f065c,(replay,))
check('replay of unreused free record underflows actual helper counter',m.read(p,4)==0xffffffff and p in freechain(m)['slots'])
again=pop(m,99)
check('subsequent actual pop wraps underflowed counter to zero',again==p and m.read(p,4)==0)
save('replay before record reuse',m,{'same_address':hex(p),'counter_after_next_pop':m.read(p,4)})

m=fresh();a=pop(m,60);cache(m,60,a);ea=raw(m,60);m.run(0x400f065c,(ea,))
bp=pop(m,64);eb=event(m,bp)
check('freed address immediately reused with new parameter data',bp==a and m.read(m.read(C+60*72+56,4)+20,4)==64)
replay=raw(m,60);m.run(0x400f065c,(replay,))
check('old cache replay frees record while newer event still points to it',m.read(eb+56,4)==bp and m.read(bp,4)==0 and bp in freechain(m)['slots'])
cp=pop(m,67);ec=event(m,cp);m.run(0x400f065c,(eb,))
check('completion of prior generation frees newest live record',cp==bp and m.read(ec+56,4)==cp and m.read(cp,4)==0 and cp in freechain(m)['slots'])
save('cross-generation reuse',m,{'A_B_C_same_address':hex(a),'old_cache_reads_tag':m.read(a+20,4)})

m=fresh();a=pop(m,60);cache(m,60,a);ea=raw(m,60);m.run(0x400f0690,(T,ea));m.run(0x400f065c,(ea,))
check('retained template protects first completed event record',m.read(a,4)==1 and a not in freechain(m)['slots'])
bp=pop(m,64);eb=event(m,bp);m.run(0x400f065c,(eb,))
replay=raw(m,60);m.run(0x400f065c,(replay,))
check('additive arp case still frees template record after unretained replay',m.read(T+56,4)==a and m.read(a,4)==0 and a in freechain(m)['slots'])
tick=event(m);m.run(0x400f0690,(tick,T))
check('later template copy increments ref but does not remove free-list entry',m.read(a,4)==1 and a in freechain(m)['slots'])
m.run(0x400f065c,(tick,))
check('release after retaining a free-list member creates a self-cycle',freechain(m)['cycle_at']==a and m.read(a+16,4)==a)
save('template retained without replacement',m,{'template':hex(T),'record':hex(a)})

m=fresh();a=pop(m,60);cache(m,60,a);ea=raw(m,60);m.run(0x400f0690,(T,ea));m.run(0x400f065c,(ea,))
bp=pop(m,64);eb=event(m,bp);m.run(0x400f0690,(T,eb));m.run(0x400f065c,(eb,))
check('template replacement frees old A and retains B',m.read(a,4)==0 and a in freechain(m)['slots'] and m.read(bp,4)==1)
replay=raw(m,60);m.run(0x400f0690,(T,replay))
check('replacing template with stale source does not fix its free-list membership',m.read(a,4)==1 and a in freechain(m)['slots'])
save('template replaced before replay',m,{'old_A':hex(a),'new_B':hex(bp)})

m=fresh();p=pop(m,64);cache(m,64,p);e=raw(m,64);m.run(0x400f065c,(e,))
check('unpublished cache first transfer releases exactly once',m.read(p,4)==0 and len(freechain(m)['slots'])==64)
save('unselected cache first publication',m,{})
m=fresh();p=pop(m,64);cache(m,64,p);cache(m,64,0)
check('unpublished cache departure leaves positive ref outside free list',m.read(p,4)==1 and p not in freechain(m)['slots'])
save('unselected cache discarded before publication',m,{'discarded_record':hex(p)})

m=fresh();busy=[event(m) for _ in range(128)];p=pop(m,60);cache(m,60,p)
check('event pool exhausted while payload still available',len(set(busy))==128 and raw(m,60)==0 and m.read(p,4)==1)
m.run(0x400f065c,(busy.pop(),));recovered=raw(m,60);m.run(0x400f065c,(recovered,))
check('failed publication can recover through later first transfer',m.read(p,4)==0 and p in freechain(m)['slots'])
save('fresh-event failure with later recovery',m,{})
m=fresh();busy=[event(m) for _ in range(128)];p=pop(m,60);cache(m,60,p);check('fresh event failure returns null',raw(m,60)==0);cache(m,60,0)
check('failure then departure leaves unreleased payload record',m.read(p,4)==1 and p not in freechain(m)['slots'])
save('fresh-event failure then cache discard',m,{'discarded_record':hex(p)})

m=fresh();busy=[event(m) for _ in range(127)];p=pop(m,60);cache(m,60,p);cache(m,64,0)
departing=raw(m,64);replacement=raw(m,60)
check('one available event permits departing copy but replacement allocation fails',departing!=0 and replacement==0 and m.read(departing+56,4)==0 and m.read(p,4)==1)
save('partial publication',m,{'departing_event':hex(departing),'replacement_event':replacement})

m=fresh()
for k in range(128):
 p=pop(m,k);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f065c,(e,));m.run(0x400f0690,(T,T+4*72))
 assert m.read(p,4)==0 and len(freechain(m)['slots'])==64
check('128 balanced lifecycle cycles restore pool without touching trailer',len(freechain(m)['slots'])==64)
save('balanced copy completion and template cleanup',m,{})
m=fresh();p=P;e=event(m,p);m.write(e,4,1);m.run(0x400f0690,(T,e));m.run(0x400f065c,(e,))
check('type-one borrowed payload bypasses common retain/release',m.read(p,4)==0 and len(freechain(m)['slots'])==64 and m.read(T,4)==1)
save('type-one borrowed payload',m,{})
source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
r={'firmware_modified':False,'sha256':hashes,'executed_stock_ranges':[[hex(x) for x in r] for r in RANGES],'scenario_executed_instructions':total_steps,'checks':checks,'scenarios':scenarios,'scope':'Actual instruction execution for payload/event allocation, release, common copy and memcpy in a custom bounded interpreter. Cache selection, event scheduling, arp acceptance and parameter-data writes are supplied scenario inputs. Not whole-firmware emulation or hardware reproduction.','limitations':['Custom bounded interpreter, not independently validated against a ColdFire emulator or hardware.','No preemption, exception injection, task scheduler, DSP or controller loop executed.','Synthetic mapped RAM layout, with constructed stock-shape free lists.','Negative scenario reachability is not proved for all outer firmware gates.']}
pathlib.Path('outputs/Digitone-payload-lifecycle-execution-results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'scenarios':len(scenarios),'executed_instructions':total_steps,'hashes_unchanged':True},indent=2))
