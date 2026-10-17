"""Read-only application/thread startup probes and actual constructor traversal."""
import pathlib,json,copy,re,hashlib
n={};text=pathlib.Path('work/test-placed-bootstrap-initializer.py').read_text();exec(text.split('\nchecks=[];cases=[]')[0],n)
exec(text[text.index('def machine():'):text.index("check('resident layout")],n)
s=n['s'];b=n['b'];base=n['base'];md=n['h']['md'];checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
class Stop(Exception):pass
s['StartupStop']=Stop
old_observe=s['observe_placed']
def observe(m,pc):
 if pc in getattr(m,'startup_stops',[]):m.stop_pc=pc;raise Stop()
 if pc==0x40000568 and getattr(m,'follow_application',False):return
 old_observe(m,pc)
s['observe_placed']=observe
src=n['src'].replace('range(300000)','range(2000000)').replace("   elif m=='swap':","   elif m=='nop':pass\n   elif m=='addx':\n    x=self.get(ops[0],n);y=self.get(ops[1],n);v=x+y+bool(self.sr&16);oldz=bool(self.sr&4);self.put(ops[1],n,v);self.flags(v,n,bool((~(x^y)&(y^v))&(1<<(8*n-1))),v>=(1<<(8*n)),True);self.sr=(self.sr&~4)|(4 if oldz and not(v&((1<<(8*n))-1)) else 0)\n   elif m=='swap':")
# No fake allocation/free returns from the inherited event-test runner.
for address in ['400dae08','400dae14']:
 src=re.sub('   if pc==0x'+address+r':\n.*?continue\n','',src,count=1,flags=re.S)
s['RANGES'].append((base,base+len(b)))
exec('if True:\n'+src,s)
class StartupMachine(s['SequenceMachine']):
 def read(self,a,z):
  if 0xec000000<=a<0xed000000 or 0xfc000000<=a<0xfd000000:return self.hardware.get(a,0)
  return super().read(a,z)
 def write(self,a,z,v):
  if 0xec000000<=a<0xed000000 or 0xfc000000<=a<0xfd000000:
   self.hardware[a]=v;self.mmio_writes.append((hex(a),z,v));return
  if base<=a and a+z<=s['clearlo']:
   for j,value in enumerate((v&((1<<(8*z))-1)).to_bytes(z,'big')):self.mem[a+j]=value
   self.writes.append((a,z,v));return
  return super().write(a,z,v)
def fresh():
 m=n['machine']();m.__class__=StartupMachine;m.hardware={};m.mmio_writes=[];m.startup_stops=[];m.run=s['run'].__get__(m,StartupMachine);s['active']=m
 owner=n['startup'](m);m.map(0x40000000,1024);m.reg['a7']=0x30002000;return m,owner
def runstop(m,entry,stops):
 m.startup_stops=stops
 try:m.run(entry)
 except Stop:return m.stop_pc
 raise AssertionError('expected stop not reached')
def protected(m,owner):return (m.read(0x4199d590,4),bytes(m.read(owner+j,1) for j in range(0x15c80)))
def allocator_state(m):
 return (bytes(m.read(0x401fe590+j,1) for j in range(20)),bytes(m.read(0x429a38c0+j,1) for j in range(84)),bytes(m.read(0x41925eb8+j,1) for j in range(0x20000)))

m,owner=fresh();snapshot=protected(m,owner);heap=allocator_state(m);start=len(m.steps)
check('application entry reaches actual first scheduler trap',runstop(m,0x4012b344,[0x4012b3be])==0x4012b3be)
check('application prefix preserves owner and entire allocation',protected(m,owner)==snapshot)
check('application prefix preserves allocator control/heads/bitmap',allocator_state(m)==heap)
check('actual startup thread saved entry is recovered function',m.read(0x41323544+0x48,4)==0x4132758c and m.read(0x41327590,4)==0x4008c4f6)
check('actual ready queue contains startup thread',m.read(0x429a3968,4)==0x41323544)
cases.append({'kind':'application to first trap','instructions':len(m.steps)-start,'stop':hex(m.stop_pc),'hardware':'register read/write dictionary; physical timer/interrupt effects absent'})

# Enter the actual saved thread PC at a scheduling boundary. No claim to have
# executed the ColdFire trap/RTE scheduler/context-switch machinery.
m.reg['a7']=0x30002000;m.sr=0x2000;start=len(m.steps)
runstop(m,m.read(0x41327590,4),[0x4008c524])
check('first startup thread creates second saved entry',m.read(0x41327598+0x48,4)==0x4132b5e0 and m.read(0x4132b5e4,4)==0x4008c634)
check('first startup thread preserves owner allocation',protected(m,owner)==snapshot)
check('first startup thread preserves allocator metadata',allocator_state(m)==heap)
cases.append({'kind':'first startup thread to spin','instructions':len(m.steps)-start,'stop':hex(m.stop_pc),'boundary':'saved PC supplied; trap/context restore not executed'})

count=int.from_bytes(b[0x40241ab4-base:0x40241ab8-base],'big');callbacks=[int.from_bytes(b[0x40241ab8-base+4*j:0x40241abc-base+4*j],'big') for j in range(count)]
pre_table_machine=copy.deepcopy(m)
# Attempt actual callback traversal starting at the real dispatcher. No callback
# immediate-return substitutions; record exact unresolved instruction if any.
m.reg['a7']=0x30002000;m.sr=0x2000;m.startup_stops=[0x4008c7f4];start=len(m.steps);completed=False;error=None
try:m.run(0x4008c7d4)
except Stop:completed=True
except (AssertionError,NotImplementedError,RuntimeError,KeyError) as exc:error=f'{type(exc).__name__}: {exc}'
callback_seen=[p for p in m.steps[start:] if p in callbacks]
check('all actual constructor callbacks execute in table order',completed and callback_seen==callbacks)
check('owner survives actually executed callback prefix',protected(m,owner)==snapshot)
check('constructor allocations keep initialized allocator flag/control',bytes(m.read(0x401fe590+j,1) for j in range(20))==heap[0])
cases.append({'kind':'actual callback dispatcher attempt','complete':completed,'callback_entries':list(map(hex,callback_seen)),'instructions':len(m.steps)-start,'actual_allocator_entries':m.steps[start:].count(0x400dab8c),'error':error,'last_pc':hex(m.steps[-1])})

def attempt(machine,entry,stops,kind):
 s['active']=machine;machine.reg['a7']=0x30002000;machine.startup_stops=stops;before=len(machine.steps);done=False;err=None
 try:machine.run(entry)
 except Stop:done=True
 except (AssertionError,NotImplementedError,RuntimeError,KeyError) as exc:err=f'{type(exc).__name__}: {exc}'
 check(kind+': executed portion preserves owner/allocation',protected(machine,owner)==snapshot)
 cases.append({'kind':kind,'complete':done,'error':err,'last_pc':hex(machine.steps[-1]),'instructions':len(machine.steps)-before,'boundary':None if not done else hex(machine.stop_pc),'hardware':'zero-default MMIO fixture, not physical hardware readiness'})
 return done
# Preserve real constructor effects when testing the post-table path.
post=copy.deepcopy(m)
shortsrc=src.replace('range(2000000)','range(50000)');exec('if True:\n'+shortsrc,s)
post.run=s['run'].__get__(post,StartupMachine)
attempt(post,0x4008c7f4,[0x400f0504],'post-table startup toward initializer')
pre_table_machine.map(0,4);pre_table_machine.run=s['run'].__get__(pre_table_machine,StartupMachine)
attempt(pre_table_machine,0x4008c634,[0x4008c7d4],'second-thread hardware setup toward table')
s['active']=m;exec('if True:\n'+src,s);m.run=s['run'].__get__(m,StartupMachine)

# Audit known direct resets and dispatcher ordering, without treating literal
# searches as proof about computed pointers or unexecuted callees.
owner_refs=[base+i for i in range(len(b)-3) if b[i:i+4]==(0x4199d590).to_bytes(4,'big')]
check('all exact stock owner literal references are in initializer',owner_refs==[0x400f0574,0x400f058e,0x400f05a0])
check('scheduler prefix clear excludes free-head table',0x429a38c0+84<=0x429a3968)
check('scheduler prefix clears exclude early owner block',owner+0x20000<=0x429a3968)
check('stock allocator initialized flag remains set after executed prefix',m.read(0x401fe590,4)==1)
check('post-table UART wait is unchanged actual instruction sequence',b[0x4009f34a-base:0x4009f358-base].hex()=='1239ec0700047404c2824a0167f2')
check('pre-table SPI wait is unchanged actual instruction sequence',b[0x400ecee6-base:0x400ecef4-base].hex()=='2039fc05c02ce888740fc08267f2')
check('original firmware unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
check('original SysEx unchanged',hashlib.sha256(pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
result={'checks':checks,'check_count':len(checks),'cases':cases,'callbacks_count':count,'owner_refs':list(map(hex,owner_refs)),'firmware_modified':False,'verification_complete':False,'limits':['Physical trap/RTE switching and asynchronous interrupts not executed.','MMIO modeled as dictionary.','Hardware setup and post-table path attempts may stop at missing instruction support or hardware-dependent waits; see cases.','Literal search does not exclude computed/bulk aliases.']}
pathlib.Path('outputs/Digitone-intervening-startup-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'checks':len(checks),'cases':cases},indent=2))
