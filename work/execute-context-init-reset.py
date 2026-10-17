"""Stock initialization/reset execution; allocator boundary explicitly supplied."""
exec(open('work/execute-cache-ordering.py').read().split('checks=[];cases=[]')[0])
source=' def run'+pathlib.Path('work/execute-payload-lifecycle.py').read_text().split(' def run',1)[1].split('\nP=',1)[0]
source=source.replace('range(20000)','range(80000)')
source=source.replace("   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)","   if pc==0x400dab8c:\n    self.allocations.append(self.read(self.reg['a7']+4,4));self.reg['d0']=self.allocation_result;pc=self.get('(a7)+',4);continue\n   if pc==0x400f0592:self.publication_witness={'owner':self.read(0x4199d590,4),'first_byte_before_clear':self.read(P,1),'free_head_before_linking':self.read(0x4199fe98,4)}\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
source=source.replace("elif m=='muls':", "elif m in ('muls','mulu'):")
source=source.replace('x=x-0x100000000 if x&0x80000000 else x;y=y-0x100000000 if y&0x80000000 else y','x=x-0x100000000 if m==\'muls\' and x&0x80000000 else x;y=y-0x100000000 if m==\'muls\' and y&0x80000000 else y')
exec('if True:\n'+source);Machine.run=run
RANGES.extend([(0x400f0504,0x400f05d6),(0x400ec284,0x400ec2ce),(0x400f08f0,0x400f0954),(0x4009713c,0x4009719e),(0x400ef9d0,0x400ef9f6),(0x4009bd6a,0x4009bd8a),(0x4009ba94,0x4009bab0)])
checks=[];cases=[]
T=0x41345f08
def check(name,c):assert c,name;checks.append(name)
def init_setup():
 m=setup();m.map(0x4199d590,0x2914);m.map(0x41342400,0x4300);m.allocations=[];m.allocation_result=P
 return m
# Stock cold path: capture publication before actual memset; extra trailer is a
# PC canary outside the stock request, not an implemented firmware extension.
m=init_setup()
for i in range(0x14100):m.write(P+i,1,0xa5)
begin=len(m.steps);m.run(0x400f0504,(158,))
check('cold initializer requests stock size',m.allocations==[0x14100])
check('stock publishes owner before clear/link',m.publication_witness=={'owner':P,'first_byte_before_clear':165,'free_head_before_linking':0})
check('all 64 stock records linked and reset',len(freechain(m)['slots'])==64 and all(m.read(P+j*0x504,4)==0 for j in range(64)))
check('stock clear excludes proposed trailer',bytes(m.mem[P+0x14100+i] for i in range(16))==TRAILER)
check('initializer returns local base pointer',m.reg['d0']==P)
cases.append({'name':'cold stock initialization','steps':len(m.steps)-begin,'allocator_requests':m.allocations,'publication_witness':m.publication_witness})
# Quiescent reentry preserves trailer but rebuilds every pool/head.
begin=len(m.steps);m.run(0x400f0504,(158,))
check('reuse does not allocate again',len(m.allocations)==1)
check('reuse preserves trailer',bytes(m.mem[P+0x14100+i] for i in range(16))==TRAILER)
cases.append({'name':'quiescent reuse','steps':len(m.steps)-begin,'trailer_preserved':True})
# Positive retained owner survives drain/reset but not pool reinitialization.
p=pop(m,60);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f065c,(e,))
check('template owns one reference after original event release',m.read(p,4)==1)
# Cache pointer remains even when cache list/bitmaps are reset.
m.write(K+0x414+60*72+56,4,p)
# Existing event pool now lives at its actual initialized fixed addresses.
e=event(m);m.run(0x400f0690,(e,T));m.run(0x400f0886,(e,))
check('published copy and template have two counted owners',m.read(p,4)==2)
begin=len(m.steps);m.run(0x4009bd6a)
check('actual drain empties published queue',m.read(0x4199fe94,4)==0)
check('actual drain preserves retained template reference',m.read(T+56,4)==p and m.read(p,4)==1)
check('bitmap/cache reset preserves cached payload pointer',m.read(K+0x414+60*72+56,4)==p)
check('bitmap/cache reset preserves template reference',m.read(T+56,4)==p and m.read(p,4)==1)
check('ordinary drain/reset preserves trailer',bytes(m.mem[P+0x14100+i] for i in range(16))==TRAILER)
cases.append({'name':'queue drain plus arp/cache bitmap reset','steps':len(m.steps)-begin,'template_reference':m.read(p,4),'cache_pointer':hex(m.read(K+0x414+60*72+56,4))})
begin=len(m.steps);m.run(0x400f0504,(158,))
check('pool reentry resets still-retained record count',m.read(T+56,4)==p and m.read(p,4)==0)
p2=pop(m,64)
check('pool reentry permits immediate alias with surviving template',p2==p and m.read(T+56,4)==p2)
check('reentry still leaves trailer intact',bytes(m.mem[P+0x14100+i] for i in range(16))==TRAILER)
cases.append({'name':'nonquiescent pool reentry negative control','steps':len(m.steps)-begin,'retained_pointer':hex(m.read(T+56,4)),'new_record':hex(p2),'count':m.read(p,4)})
# Null allocator return: stock has no failure branch before clearing.
m=init_setup();m.allocation_result=0
try:m.run(0x400f0504,(158,));raise AssertionError('null allocation unexpectedly completed')
except RuntimeError as exc:
 check('null reaches write through zero in bounded RAM', 'unmapped write 00000000/4' in str(exc))
 check('null owner was published without success guard',m.read(0x4199d590,4)==0 and m.publication_witness['owner']==0)
 cases.append({'name':'null allocator boundary','diagnostic':str(exc),'publication_witness':m.publication_witness})
# Proposed protocol only: fail closed at all cold/reentry intermediate states.
protocol=[]
for existing in [False,True]:
 owner=P if existing else 0;ready=False
 for phase in ['disabled','record_setup','trailer_setup','complete']:
  if phase=='complete':owner=P;ready=True
  allowed=bool(owner and ready)
  check('proposal disallows reads until complete',allowed==(phase=='complete'))
  protocol.append({'existing_owner':existing,'phase':phase,'capture_allowed':allowed})
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
pathlib.Path('outputs/Digitone-context-init-reset-results.json').write_text(json.dumps({'firmware_modified':False,'checks':checks,'cases':cases,'proposed_protocol_specification':protocol,'sha256':hashes,'limitations':['Allocator itself is not executed: its return value is explicitly supplied at 400dab8c.','Normal reset wrapper and callback execute with a type-zero event; type-three external-pool callback branch is untested.','No live reentry reachability or interrupt scheduler proof.','Trailer is a PC canary; no extended allocation/hook implemented.','Custom interpreter not independently hardware validated.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'steps':sum(c.get('steps',0) for c in cases),'hashes_unchanged':True}))
