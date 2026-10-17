"""Resume saved, byte-validated decompression state with correct ColdFire A7."""
import pathlib,pickle,json,collections,hashlib
p=pathlib.Path('work/test-startup-completions.py').read_text();exec(p.split("for mode in ['ready'")[0])
response_observe=s['observe_placed']
def fast_observe(m,pc):
 if pc in getattr(m,'startup_stops',[]):m.stop_pc=pc;raise t['Stop']()
 if pc in [0x400ec45c,0x400ece52,0x40000568,0x4009bcc4,0x400dab8c,0x400ec284,0x4000054c,t['n']['SPIN']] or 0x400f0504<=pc<0x400f05d6 or getattr(m,'code_start',0)<=pc<getattr(m,'code_end',0):response_observe(m,pc)
s['observe_placed']=fast_observe
class CachedMD:
 def __init__(self,real):self.real=real;self.cache={}
 def disasm(self,data,pc,count=0):
  key=(pc,bytes(data))
  if key not in self.cache:self.cache[key]=list(self.real.disasm(data,pc,count=count))
  return iter(self.cache[key])
s['md']=CachedMD(s['md'])
# Correct only the explicitly documented byte adjustment; firmware untouched.
methods=pathlib.Path('work/execute-payload-lifecycle.py').read_text()
getsrc=methods[methods.index(' def get('):methods.index(' def flags(')]
assert getsrc.count("2 if n==1 and r=='a7' else n") in [0,4]
getsrc=getsrc.replace("2 if n==1 and r=='a7' else n",'n')
exec('if True:\n'+getsrc,s);ResponseMachine.get=s['get'];ResponseMachine.put=s['put']
# Tests include exact accessed address, pointer delta, and preserved guards.
q,_=new();q.map(0x29000000,32)
for reg in ['a0','a7']:
 for width in [1,2,4]:
  q.reg[reg]=0x29000010;q.put(f'-({reg})',width,0x5a);check(f'{reg} predecrement width {width}',q.reg[reg]==0x29000010-width and q.read(0x29000010-width,width)==0x5a)
  q.reg[reg]=0x29000010;q.write(0x29000010,width,0x6b);value=q.get(f'({reg})+',width);check(f'{reg} postincrement width {width}',value==0x6b and q.reg[reg]==0x29000010+width)
state=pickle.loads(pathlib.Path('work/post-decompression-state.pkl').read_bytes());m,_=new();m.__dict__.update(state['attrs']);owner=state['owner'];snapshot=state['owner_before'];s['active']=m
oldwrite=ResponseMachine.write;m.cleanup_writes=collections.deque(maxlen=3000)
def tracedwrite(self,a,z,v):
 if 0x30001e80<a+z and a<0x30002000:self.cleanup_writes.append((self.steps[-1] if self.steps else 0,a,z,v))
 return oldwrite(self,a,z,v)
ResponseMachine.write=tracedwrite
frame="  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry"
adv=src.replace('def run(self,entry,args=()):','def advance(self,entry,args=()):').replace(frame,'  pc=entry').replace('range(2000000)','range(10000000)')
exec('if True:\n'+adv,s);m.advance=s['advance'].__get__(m,ResponseMachine)
m.startup_stops=[0x400f0504];before=len(m.steps);outcome=None
try:m.advance(0x400ee416)
except t['Stop']:outcome='initializer reached'
except Exception as e:outcome=f'{type(e).__name__}: {e}'
check('corrected continuation preserves proposed allocation',t['protected'](m,owner)==snapshot)
results={'check_count':len(checks),'checks':checks,'firmware_modified':False,'continuation':{'outcome':outcome,'instructions':len(m.steps)-before,'last_pc':hex(m.steps[-1]),'regs':m.reg.copy(),'last_instructions':[hex(pc) for pc in m.steps[-100:]],'stack_words':[(hex(m.reg['a7']+j),hex(m.read(m.reg['a7']+j,4))) for j in range(0,96,4)]},'cleanup_writes':[(hex(pc),hex(a),z,hex(v&((1<<(8*z))-1))) for pc,a,z,v in m.cleanup_writes]}
attrs={k:v for k,v in m.__dict__.items() if k not in ['run','advance','steps','writes','timeline']};attrs.update(steps=m.steps[-100:],writes=[],timeline=[]);pathlib.Path('work/corrected-cleanup-state.pkl').write_bytes(pickle.dumps({'attrs':attrs,'owner':owner,'owner_before':snapshot},protocol=5))
pathlib.Path('outputs/Digitone-corrected-stack-pointer-results.json').write_text(json.dumps(results,indent=2));print(json.dumps({'checks':len(checks),'continuation':results['continuation']},indent=2),flush=True)
