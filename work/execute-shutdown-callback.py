"""Bounded callback-to-setup trace; firmware remains unchanged."""
exec(open('work/execute-payload-lifecycle.py').read().split('checks=[];scenarios=[];total_steps=0')[0])
source=' def run'+pathlib.Path('work/execute-payload-lifecycle.py').read_text().split(' def run',1)[1].split('\nP=',1)[0]
source=source.replace('def run(self,entry,args=()):','def until(self,entry,stop):')
source=source.replace("  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry","  pc=entry")
source=source.replace('if pc==0xffffffff:break','if pc==stop:break')
source=source.replace("   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)","   if pc==0x400dae08:\n    self.allocator_calls.append(self.read(self.reg['a7']+4,4));self.reg['d0']=0x27008000;pc=self.get('(a7)+',4);continue\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
source=source.replace("  self.reg['a7']+=len(args)*4",'').replace("  assert self.reg['a7']==initial_sp",'').replace("  assert all(self.reg[r]==v for r,v in saved.items())",'')
exec('if True:\n'+source);Machine.until=until
RANGES.extend([(0x400d6db6,0x400d6e16),(0x4015a3ae,0x4015a40a),(0x400ae502,0x400ae554),(0x400ae45e,0x400ae464),(0x4009c802,0x4009c80c),(0x4009bcc6,0x4009bd6a),(0x4009bcb8,0x4009bcc6),(0x400d95cc,0x400d95ee),(0x400012c8,0x400012e2),(0x4008afee,0x4008affc)])
checks=[];cases=[]
def check(name,c):assert c,name;checks.append(name)
def setup_state():
 m=fresh();m.allocator_calls=[]
 for a,n in [(0x27000000,0x8100),(0x401f21e0,4),(0x401fdd10,4),(0x40253e80,4),(0x400002b8,4),(0x400002fc,4),(0xfc04c01c,2),(0xfc04c07f,1),(0x4199d590,4)]:m.map(a,n)
 m.write(0x4199d590,4,P)
 return m
# Existing page-entry helper installs alternate handlers without touching pool.
m=setup_state();m.run(0x400d95cc)
check('alternate handler installed',m.read(0x400002fc,4)==0x400d924e)
check('alternate timer handler installed',m.read(0x400002b8,4)==0x400d920c)
check('entry helper preserves caller interrupt mask',m.sr&0xff00==0x2000)
check('entry helper leaves persistent owner alone',m.read(0x4199d590,4)==P)
cases.append({'name':'alternate handler installation','steps':len(m.steps),'handler':hex(m.read(0x400002fc,4)),'sr':hex(m.sr)})
# Shape comes from actual constructor: std-function record in exit vector.
# One controlled entry, empty closure; memory allocator return supplied.
O=0x27000000;V=0x27001000
m.write(O+0x40,4,V);m.write(O+0x44,4,V+16);m.write(O+0x48,4,V+16)
m.write(V,4,0x27002000);m.write(V+8,4,0x400ae502);m.write(V+12,4,0x400ae45e)
p=pop(m,60);m.write(T+56,4,p) # A controlled retained owner outside the queue.
start=len(m.steps);m.put('-(a7)',4,O);m.put('-(a7)',4,0xffffffff)
m.until(0x400d6db6,0x400f0504)
check('exit vector reaches common initializer',m.steps[-1]==0x4009bcbc)
check('exit path reaches initializer with caller mask unchanged',m.sr&0xff00==0x2000)
check('alternate handler remains installed at initializer boundary',m.read(0x400002fc,4)==0x400d924e)
check('retained payload remains live at initializer boundary',m.read(p,4)==1 and m.read(T+56,4)==p)
check('actual callable-copy manager requests one byte',m.allocator_calls==[1])
check('exit did not drain or rebuild pools before initializer',not any(a in m.steps[start:] for a in [0x4009bd6a,0x400f08f0,0x400f0504]))
cases.append({'name':'exit-vector dispatch before pool initialization','steps':[hex(x) for x in m.steps[start:]],'sr':hex(m.sr),'handler':hex(m.read(0x400002fc,4)),'retained_count':m.read(p,4),'allocation_requests':m.allocator_calls})
# Matched test-exit command's post-comparison route; string comparison omitted.
m=setup_state();m.write(0x400002fc,4,0x4008dce0);m.write(0x40253e80,4,1)
m.put('-(a7)',4,0xffffffff);m.until(0x4008afee,0x400f0504)
check('test exit clears mode flag before setup',m.read(0x40253e80,4)==0)
check('test exit preserves mask before initializer',m.sr&0xff00==0x2000)
check('test alternate handler remains at initializer boundary',m.read(0x400002fc,4)==0x4008dce0)
cases.append({'name':'matched test-exit command continuation','steps':[hex(x) for x in m.steps],'sr':hex(m.sr),'handler':hex(m.read(0x400002fc,4))})
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx');hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
check('source hashes unchanged',hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'])
pathlib.Path('outputs/Digitone-shutdown-callback-execution-results.json').write_text(json.dumps({'firmware_modified':False,'checks':checks,'cases':cases,'sha256':hashes,'scope':'Actual exit-vector copy/dispatch and setup route stopped at initializer entry; controlled callback list and configuration flag 401f21e0 zero. Existing handler installation executed separately.','limitations':['Allocator return supplied for one-byte empty-closure copy.','No actual UI scheduler, MIDI task, audio interrupt or peripheral execution.','Configuration flags and entry SR are controlled inputs, not proven hardware state.','Retained template is a controlled owner; this test does not establish normal page entry retains one.','No general transitive shutdown or exception cleanup certification.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'steps':sum(len(c['steps']) if isinstance(c['steps'],list) else c['steps'] for c in cases),'hashes_unchanged':True}))
