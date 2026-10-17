"""PC-only resident layout, real helper writes around the stock setup/copy caller."""
exec(open('work/test-metadata-helper-instructions.py').read().split('checks=[];total=0;record=')[0])
# Helper bodies contain only local branches, so relocation needs no absolute fixups.
oldfixtures=fixtures.copy();oldnames=names.copy();fixtures={};names={};cursor=0x40241ca0
for name,old in oldnames.items():
 if name in ('copy','invalidate'):continue
 names[name]=cursor;fixtures[cursor]=oldfixtures[old];cursor+=len(oldfixtures[old])
def u32(x):return x.to_bytes(4,'big')
def absolute(a,op,target):a.emit(op);a.code.extend(u32(target))
def add(name,a):
 global cursor
 names[name]=cursor;fixtures[cursor]=a.done();cursor+=len(fixtures[names[name]])
# Resolve accepted-record address from actual owner, with header/readiness checks.
# d0=playback track; result a0=record or null. No argument frame.
a=Asm();a.emit('0c8000000004');a.branch('6400','none');a.emit('20794199d590');a.emit('4a88');a.branch('6700','none');a.emit('2248d3fc000141000c91534c4332');a.branch('6600','none');a.emit('0ca9000400000002') # corrected below: CMPI imm precedes displacement
# Replace last encoding with correct cmpi.l #2,4(a1).
a.code[-8:]=bytes.fromhex('0ca9000000020004')
a.branch('6600','none');a.emit('0ca900000b700008');a.branch('6600','none');a.emit('0ca900000001000c');a.branch('6600','none');a.emit('e988d1fc00014c30d1c0');a.branch('6000','end');a.label('none');a.emit('91c8');a.label('end');a.emit('4e75');add('resolve',a)
# Known fixed event-pool entry only; no division or use of payload ownership.
# (event*) stack argument -> snapshot word in d0. Header checked by caller.
a=Asm();a.emit('20794199d590d1fc00014120226f0004223c00000080')
# a1 initially event argument; d0 is walking real event-pool address.
a.emit('203c4199da94');a.label('loop');a.emit('b3c0');a.branch('6700','found');a.emit('06800000004841e800045381');a.branch('6600','loop');a.emit('4280');a.branch('6000','end');a.label('found');a.emit('2010');a.label('end');a.emit('4e75');add('snapshot',a)
def save(a):a.emit('4fefffc048d77fff40c03f40003c')
def restore(a):a.emit('302f003c46c04cd77fff4fef0040')
# Before setup wrapper: preserve original ABI and replace existing return address.
a=Asm();save(a);a.emit('202f0044');absolute(a,'4eb9',names['resolve']);a.emit('4a88');a.branch('6700','restore');a.emit('2f08');absolute(a,'4eb9',names['begin']);a.emit('588f');a.label('restore');restore(a)
# after address is fixed once the preceding body length is known.
BEFORE=cursor;after_addr=cursor+len(a.code)+12
absolute(a,'2ebc',after_addr);absolute(a,'4ef9',0x4009719e);add('before',a)
a=Asm();save(a);a.emit('20174a80');a.branch('6600','restore');a.emit('202f0040');absolute(a,'4eb9',names['resolve']);a.emit('4a88');a.branch('6700','restore');a.emit('2f08');absolute(a,'4eb9',names['cancel']);a.emit('588f');a.label('restore');restore(a);absolute(a,'4ef9',0x4009ddac);assert cursor==after_addr;add('after',a)
# Commit at real retained-copy completion; displaced instructions replayed.
a=Asm();save(a);a.emit('202b0008');absolute(a,'4eb9',names['resolve']);a.emit('4a88');a.branch('6700','restore');a.emit('24482f2b00082f0b');absolute(a,'4eb9',names['snapshot']);a.emit('588f2f002f2b00402f0a');absolute(a,'4eb9',names['commit']);a.emit('4fef0010');a.label('restore');restore(a);a.emit('202b000841f941345ef8');absolute(a,'4ef9',0x4009de50);add('caller_commit',a)

# Preflight replays stock pushes before allocation; d2 holds owner only temporarily.
# Helper initialization requires cold boot owner zero; reentry uses the already extended owner.
a=Asm();a.emit('2f032f020caf0000009e000c');a.branch('6600','failure');a.emit('20394199d590');a.branch('6600','resume');a.emit('2f3c00014c70');absolute(a,'4eb9',0x400dab8c);a.emit('588f2400');a.branch('6700','failure');a.emit('2f3c00014c7042a72f00');absolute(a,'4eb9',0x400ec284);a.emit('4fef000c2042d1fc0001410020bc534c4332217c000000020004217c00000b70000823c24199d590');a.label('resume');a.emit('41f94199dad8');absolute(a,'4ef9',0x400f050e);a.label('failure');a.emit('46fc270060fe');add('init_preflight',a)
a=Asm();a.emit('40c120794199d590d1fc0001410c20bc0000000146c1241f261f4e75');add('init_ready',a)

assert cursor<=0x40242000,hex(cursor)
# Synthetic overlay fetch. Only these fixtures shadow original zero padding;
# the original b/file is never modified. Stock caller call is intercepted in fetch.
overlay_enabled=True
def fetch(pc):
 if not overlay_enabled:return b[pc-base:pc-base+16]
 for addr,code in fixtures.items():
  if addr<=pc<addr+len(code):return code[pc-addr:pc-addr+16]
 if pc==0x400f0504:return bytes.fromhex('4ef9')+u32(names['init_preflight'])+bytes.fromhex('4e714e71')
 if pc==0x400f05d0:return bytes.fromhex('4ef9')+u32(names['init_ready'])
 if pc==0x4009dda6:return bytes.fromhex('4eb9')+u32(names['before'])
 if pc==0x4009de46:return bytes.fromhex('4ef9')+u32(names['caller_commit'])+bytes.fromhex('4e714e71')
 return b[pc-base:pc-base+16]
RANGES.extend((a,a+len(code)) for a,code in fixtures.items())
source=source.replace('range(20000)','range(80000)')
source=source.replace("   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)","   if pc==0x400dab8c:\n    self.allocations.append(self.read(self.reg['a7']+4,4));self.reg['d0']=self.allocation_result;pc=self.get('(a7)+',4);continue\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
RANGES.extend([(0x400f0504,0x400f05d6),(0x400ec284,0x400ec2ce)])
src=source.replace('b[pc-base:pc-base+16]','fetch(pc)');exec('if True:\n'+src);Machine.run=run
rtsrc=route_source.replace('b[pc-base:pc-base+16]','fetch(pc)');exec('if True:\n'+rtsrc);Machine.route=route
# Validate full decode including the known Capstone missing TST address form.
for addr,code in fixtures.items():
 items=list(md.disasm(code,addr));assert sum(i.size for i in items)==len(code)
 assert all(i.id or bytes(i.bytes)==bytes.fromhex('4a88') for i in items)
checks=[];cases=[];OWNER=0x28000000;POOL=0x4199da94
def cold_machine(result=OWNER):
 m=create();m.map(OWNER,0x14c70);m.map(0x4199d590,0x7000);m.write(0x4199d590,4,0);m.allocations=[];m.allocation_result=result
 for j in range(0x14c70):m.write(OWNER+j,1,0xa5)
 return m
m=cold_machine();m.run(0x400f0504,(158,))
check('actual preflight explicitly allocates extended metadata owner',m.allocations==[0x14c70] and m.read(0x4199d590,4)==OWNER)
check('actual initialization publishes ready header',all(m.read(OWNER+0x14100+off,4)==val for off,val in [(0,0x534c4332),(4,2),(8,0xb70),(12,1)]))
check('stock initializer clears and links original 64 records',m.read(0x4199fe98,4)==OWNER and all(m.read(OWNER+j*0x504+16,4)==(OWNER+(j+1)*0x504 if j<63 else 0) for j in range(64)))
check('actual clear initializes whole metadata table',all(m.mem[OWNER+0x14120+j]==0 for j in range(0xb50)))
import copy
initialized_owner_machine=copy.deepcopy(m)
case={'kind':'cold instruction initialization','steps':len(m.steps),'allocation_requests':m.allocations};cases.append(case)
m.write(OWNER+0x14c30,4,73);m.write(OWNER+0x14c38,4,1);beforetable=bytes(m.mem[OWNER+0x14100+j] for j in range(0xb70));beforesteps=len(m.steps)
m.run(0x400f0504,(158,))
check('actual reentry keeps table and does not allocate',bytes(m.mem[OWNER+0x14100+j] for j in range(0xb70))==beforetable and m.allocations==[0x14c70])
cases.append({'kind':'instruction initializer reentry','steps':len(m.steps)-beforesteps})
m=cold_machine(0);writes_before=len(m.writes)
try:m.run(0x400f0504,(158,))
except RuntimeError as exc:check('null allocation reaches non-returning local endpoint',str(exc)=='instruction budget exceeded')
else:raise AssertionError('null initialization returned')
check('null allocation does not publish owner or mutate pool/table',m.read(0x4199d590,4)==0 and all(0x30000000<=addr<0x30003000 for addr,n,v in m.writes[writes_before:]) and m.sr==0x2700)
cases.append({'kind':'null instruction initialization','steps':len(m.steps),'endpoint':'mask-and-spin; hardware recovery unverified'})
m=cold_machine();writes_before=len(m.writes)
try:m.run(0x400f0504,(157,))
except RuntimeError as exc:check('wrong record geometry fails before allocation or pool mutation',str(exc)=='instruction budget exceeded' and not m.allocations and all(0x30000000<=addr<0x30003000 for addr,n,v in m.writes[writes_before:]))
else:raise AssertionError('wrong geometry returned')
cases.append({'kind':'unsupported initializer geometry','steps':len(m.steps),'endpoint':'mask-and-spin'})
for track,kind in [(t,k) for t in range(4) for k in ['new','additive','rejected','replace','off','unknown_event','missing_context','not_ready','null_owner','bad_magic']]+[(0,'cold_connected')]:
 if kind=='cold_connected':m=copy.deepcopy(initialized_owner_machine)
 else:
  m=create();m.map(OWNER,0x14c70);m.map(0x4199d590,4);m.write(0x4199d590,4,OWNER);m.map(POOL,128*72)
  for j in range(128):m.write(POOL+j*72+68,4,POOL+(j+1)*72 if j<127 else 0)
  m.write(0x4199fea0,4,POOL)
 H=OWNER+0x14100;REC=OWNER+0x14c30+track*16
 if kind!='cold_connected':
  for off,val in [(0,0x534c4332),(4,2),(8,0xb70),(12,1)]:m.write(H+off,4,val)
 oldword=0x80000080|(track<<13);newword=0x80000082|(track<<13)
 if kind in ('additive','rejected','replace'):setup_call(m,track=track)
 oldid=m.read(STATE+track*40+24,4)
 if kind!='cold_connected':
  for off,val in [(0,oldid),(4,oldword),(8,0),(12,0x80000000|track)]:m.write(REC+off,4,val)
 if kind=='off':m.write(SET+0x10f,1,0)
 if kind=='not_ready':m.write(H+12,4,0)
 if kind=='bad_magic':m.write(H,4,0)
 if kind=='null_owner':m.write(0x4199d590,4,0)
 settings=SET
 if kind=='replace':settings=SET+0x200;m.write(settings+0x10f,1,1)
 e=event(m)
 if kind=='unknown_event':e=EV;m.map(e,72)
 for off,val in [(4,1),(8,track),(12,1 if kind=='rejected' else 2),(20,1),(40,0),(52,0)]:m.write(e+off,4,val)
 m.write(e+24,1,64);m.write(RETAINED+track*72+64,4,oldid)
 m.write(OWNER+0x14120,4,0 if kind=='missing_context' else newword)
 m.reg['a6']=0x30001800;m.reg['a3']=e;m.reg['a4']=NODE;m.reg['a5']=settings;m.reg['a2']=0x800034c4;m.sr=0x2510
 import copy
 baseline=copy.deepcopy(m)
 before=m.reg.copy();initialsp=m.reg['a7'];observed=[];steps_before=len(m.steps)
 def observe(pc):
  if m.read(REC+8,4)==0 and m.read(REC+12,4)==(0x80000000|track):observed.append((len(m.steps)-1,pc,m.read(REC,4),m.read(REC+4,4)))
 m.observe=observe;case_start=len(m.steps)
 m.route(0x4009dd80,0x4009ddb0);ret=m.reg['d0']
 if ret:m.route(0x4009ddb0,0x4009de50)
 else:m.route(0x4009ddb0,0x4009df0a)
 replay={'d0':m.reg['d0'],'a0':m.reg['a0']}
 overlay_enabled=False;baseline.route(0x4009dd80,0x4009ddb0)
 if ret:baseline.route(0x4009ddb0,0x4009de50)
 else:baseline.route(0x4009ddb0,0x4009df0a)
 overlay_enabled=True
 check('wrapped caller matches stock registers and exact SR',m.reg==baseline.reg and m.sr==baseline.sr)
 check('wrapped caller leaves identical retained event bytes',all(m.mem[RETAINED+track*72+j]==baseline.mem[RETAINED+track*72+j] for j in range(72)))
 valid_owner=kind not in ('null_owner','not_ready','bad_magic')
 expected=oldword if not ret or not valid_owner else 0 if kind in ('missing_context','unknown_event') else newword
 if m.read(REC+4,4)!=expected or m.read(REC+8,4)!=0:print('FAILED CASE',kind,ret,hex(m.read(REC+4,4)),m.read(REC+8,4),hex(expected),[n for n,a in names.items() if a in m.steps])
 check('actual caller produces expected metadata',m.read(REC+4,4)==expected and m.read(REC+8,4)==0)
 check('wrapper helper execution matches guard state',(names['begin'] in m.steps)==valid_owner)
 if not ret and oldid and valid_owner:check('zero-result path preserves readable prior binding',m.run(names['read'],(REC,oldid,track))==oldword)
 if ret and valid_owner:
  check('actual retained copy precedes instruction commit',m.steps.index(0x400f0690)<m.steps.index(names['commit']) and m.read(REC,4)==ret and m.read(RETAINED+track*72+64,4)==ret)
  check('reader helper sees committed word',m.run(names['read'],(REC,ret,track))==expected)
  entry=m.steps.index(0x4009719e,case_start);exitidx=m.steps.index(names['commit'])
  check('gate hides intervening stock mutation',not any(entry<=idx<exitidx for idx,pc,i,w in observed))
 check('pending caller arguments preserved',m.reg['a7']==initialsp-(8 if ret else 0))
 if ret:
  check('displaced instructions replayed',replay=={'d0':track,'a0':0x41345ef8})
 cases.append({'track':track,'kind':kind,'setup_return':ret,'metadata_identity':m.read(REC,4),'snapshot':hex(m.read(REC+4,4)),'steps':len(m.steps)-steps_before,'metadata_helpers_executed':[n for n,a in names.items() if a in m.steps]})
result={'passed':len(checks),'checks':checks,'cases':cases,'instructions':sum(c['steps'] for c in cases),'layout_start':'0x40241ca0','layout_end_exclusive':hex(cursor),'bytes_used':cursor-0x40241ca0,'remaining_gap':0x40242000-cursor,'fixtures':{name:{'address':hex(addr),'size':len(fixtures[addr]),'disassembly':[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(fixtures[addr],addr)]} for name,addr in names.items()},'firmware_modified':False,'limits':['Fetch overlay only; no firmware patch','Cold initialization executes actual wrapper/stores with supplied allocator return; caller tests supply initialized owner and candidate snapshots','All four synth tracks; controlled single-note mode one and empty voice-stop mask','Custom CPU interpreter, no cache/hardware/asynchronous producer simulation','Allocator return still supplied; stock allocator not executed; null endpoint is mask-and-spin, not graceful recovery','Padding ownership based on recovered boundaries; complete computed alias exclusion not established']}
pathlib.Path('outputs/Digitone-resident-caller-helper-tests.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'checks; layout',result['bytes_used'],'bytes, gap remaining',result['remaining_gap'])







