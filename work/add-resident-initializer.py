p='work/test-resident-caller-helpers.py';s=open(p).read()
s=s.replace("for name,old in oldnames.items():\n names", "for name,old in oldnames.items():\n if name in ('copy','invalidate'):continue\n names")
# Build initialization before the fixture assertion/fetch definition.
insertion="""
# Preflight replays stock pushes before allocation; d2 holds owner only temporarily.
# Helper initialization requires cold boot owner zero; reentry uses the already extended owner.
a=Asm();a.emit('2f032f0220394199d590');a.branch('6600','resume');a.emit('2f3c00014c70');absolute(a,'4eb9',0x400dab8c);a.emit('588f2400');a.branch('6700','failure');a.emit('2f3c00014c7042a72f00');absolute(a,'4eb9',0x400ec284);a.emit('4fef000c2042d1fc0001410020bc534c4332217c000000020004217c00000b70000823c24199d590');a.label('resume');a.emit('41f94199d594');absolute(a,'4ef9',0x400f050e);a.label('failure');a.emit('46fc270060fe');add('init_preflight',a)
a=Asm();a.emit('20794199d590d1fc0001410c20bc00000001241f261f4e75');add('init_ready',a)
"""
s=s.replace('assert cursor<=0x40242000,hex(cursor)',insertion+'\nassert cursor<=0x40242000,hex(cursor)')
s=s.replace(" if pc==0x4009dda6:", " if pc==0x400f05d0:return bytes.fromhex('4ef9')+u32(names['init_ready'])\n if pc==0x4009dda6:")
# Allocator boundary explicitly supplied; real memset and initializer execution.
s=s.replace("src=source.replace('b[pc-base:pc-base+16]','fetch(pc)');", "source=source.replace('range(20000)','range(80000)')\nsource=source.replace(\"   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)\",\"   if pc==0x400dab8c:\\n    self.allocations.append(self.read(self.reg['a7']+4,4));self.reg['d0']=self.allocation_result;pc=self.get('(a7)+',4);continue\\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)\")\nRANGES.extend([(0x400f0504,0x400f05d6),(0x400ec284,0x400ec2ce)])\nsrc=source.replace('b[pc-base:pc-base+16]','fetch(pc)');")
# Set up actual cold init tests before caller fixtures.
s=s.replace("for kind in ['new'", """def cold_machine(result=OWNER):
 m=create();m.map(OWNER,0x14c70);m.map(0x4199d590,0x2914);m.write(0x4199d590,4,0);m.allocations=[];m.allocation_result=result
 for j in range(0x14c70):m.write(OWNER+j,1,0xa5)
 return m
m=cold_machine();m.run(names['init_preflight'],(158,))
check('actual preflight explicitly allocates extended metadata owner',m.allocations==[0x14c70] and m.read(0x4199d590,4)==OWNER)
check('actual initialization publishes ready header',all(m.read(OWNER+0x14100+off,4)==val for off,val in [(0,0x534c4332),(4,2),(8,0xb70),(12,1)]))
check('stock initializer clears and links original 64 records',m.read(0x4199fe98,4)==OWNER and all(m.read(OWNER+j*0x504+16,4)==(OWNER+(j+1)*0x504 if j<63 else 0) for j in range(64)))
check('actual clear initializes whole metadata table',all(m.mem[OWNER+0x14120+j]==0 for j in range(0xb50)))
case={'kind':'cold instruction initialization','steps':len(m.steps),'allocation_requests':m.allocations};cases.append(case)
m.write(OWNER+0x14c30,4,73);m.write(OWNER+0x14c38,4,1);beforetable=bytes(m.mem[OWNER+0x14100+j] for j in range(0xb70));beforesteps=len(m.steps)
m.run(names['init_preflight'],(158,))
check('actual reentry keeps table and does not allocate',bytes(m.mem[OWNER+0x14100+j] for j in range(0xb70))==beforetable and m.allocations==[0x14c70])
cases.append({'kind':'instruction initializer reentry','steps':len(m.steps)-beforesteps})
m=cold_machine(0);writes_before=len(m.writes)
try:m.run(names['init_preflight'],(158,))
except RuntimeError as exc:check('null allocation reaches non-returning local endpoint',str(exc)=='instruction budget exceeded')
else:raise AssertionError('null initialization returned')
check('null allocation does not publish owner or mutate pool/table',m.read(0x4199d590,4)==0 and all(0x30000000<=addr<0x30003000 for addr,n,v in m.writes[writes_before:]) and m.sr==0x2700)
cases.append({'kind':'null instruction initialization','steps':len(m.steps),'endpoint':'mask-and-spin; hardware recovery unverified'})
for kind in ['new'""")
s=s.replace("'Cold initializer not yet a machine-code wrapper'", "'Allocator return still supplied; stock allocator not executed; null endpoint is mask-and-spin, not graceful recovery'")
open(p,'w').write(s)
