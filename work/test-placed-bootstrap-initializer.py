"""Resident-address fetch overlays and actual stock initializer, PC only."""
import pathlib,json,hashlib,re,copy
n={};exec(pathlib.Path('work/test-machine-bootstrap.py').read_text().split("\ns['fixtures'][ENTRY]=code")[0],n)
h,s=n['h'],n['s'];Asm=h['Asm'];absolute=h['absolute'];layout=n['layout'];entries=n['entries'];stage=n['stage']
BOOT=0x40241ca0;TABLE=0x40241e28;CLEAR1=0x40241f00;CLEAR2=0x40241f36;START=0x40241f6c;DISPATCH=0x40241f7e;TRAMP=0x40241f94
INIT_OFFSET=1678
# RAM wrapper: guard the real argument and metadata before stock mutation;
# hold interrupts masked across complete stock initializer and readiness.
a=Asm();h['save'](a);a.emit('46fc27000caf0000009e0044');a.branch('6600','fail')
a.emit('20794199d5904a88');a.branch('6700','fail');a.emit('2248d3fc000141000c91534c4332');a.branch('6600','fail')
a.emit('0ca9000000020004');a.branch('6600','fail');a.emit('0ca900000b700008');a.branch('6600','fail')
# Clearing from ready through accepted records prevents stale context on reentry.
a.emit('d1fc0001410c2f3c00000b6442a72f08');absolute(a,'4eb9',0x400ec284);a.emit('4fef000c2f2f0044');absolute(a,'4eb9',TRAMP);a.emit('588f2f400000')
a.emit('20794199d590d1fc0001410c20bc00000001');h['restore'](a);a.emit('4e75');a.label('fail');a.emit('46fc2700');a.label('spin');a.emit('60fe')
initcode=a.done();INIT_SPIN_OFFSET=INIT_OFFSET+a.labels['spin'];extension=bytearray(n['extension']);extension[INIT_OFFSET:INIT_OFFSET+len(initcode)]=initcode;extension=bytes(extension)
size=INIT_OFFSET+len(initcode)
# Reassemble bootstrap with the final extension checksum and true resident calls.
build=pathlib.Path('work/test-machine-bootstrap.py').read_text();build=build[build.index("a=h['Asm']();"):build.index("\ns['fixtures'][ENTRY]=code")]
build=build.replace('0x50030000','CLEAR1').replace('0x50030100','CLEAR2').replace('4fef000c2f420000','4fef000c23c24199d5902f420000')
g={'h':h,'s':s,'extension':extension,'stage':stage,'entries':entries,'size':size,'ENTRY':BOOT,'TABLE':TABLE,'CLEAR1':CLEAR1,'CLEAR2':CLEAR2}
exec(build,g);bootcode=g['code'];FAIL=BOOT+g['a'].labels['failure'];SPIN=BOOT+g['a'].labels['spin']
assert len(bootcode)==392
table=n['table'];assert TABLE==BOOT+len(bootcode) and TABLE+len(table)==CLEAR1
clear1=s['fixtures'][0x50030000];clear2=s['fixtures'][0x50030100]
a=Asm();absolute(a,'4eb9',BOOT);a.emit('41f9fc044000');absolute(a,'4ef9',0x4000054c);startcode=a.done()
a=Asm();a.emit('20794199d5904a88');a.branch('6700','fail');a.emit('d1fc'+(0x14c80+INIT_OFFSET).to_bytes(4,'big').hex()+'4ed0');a.label('fail');absolute(a,'4ef9',FAIL);dispatch=a.done()
# Dispatch grew beyond its initial 20-byte estimate; place trampoline after it.
assert len(dispatch)==26
TRAMP2=DISPATCH+len(dispatch)
assert TRAMP2==0x40241f98
# Fix RAM wrapper's trampoline literal and regenerate checksummed bootstrap.
initcode=initcode.replace(TRAMP.to_bytes(4,'big'),TRAMP2.to_bytes(4,'big'));extension=bytearray(extension);extension[INIT_OFFSET:INIT_OFFSET+len(initcode)]=initcode;extension=bytes(extension);g['extension']=extension;exec(build,g);bootcode=g['code']
tramp=bytes.fromhex('2f032f0241f94199dad8')+bytes.fromhex('4ef9')+(0x400f050e).to_bytes(4,'big')
blocks={BOOT:bootcode,TABLE:table,CLEAR1:clear1,CLEAR2:clear2,START:startcode,DISPATCH:dispatch,TRAMP2:tramp}
usedend=max(a+len(v) for a,v in blocks.items());assert usedend<=0x40242000
ordered=sorted(blocks.items());assert all(a+len(v)<=b for (a,v),(b,w) in zip(ordered,ordered[1:]))
b=s['b'];base=s['base'];assert not any(b[BOOT-base:0x40242000-base]);assert int.from_bytes(b[0x40241ab4-base:0x40241ab8-base],'big')==119
# Original startup call plus following LEA occupy ten bytes. Overlay replays
# both and returns to the next intact instruction, not the middle of the LEA.
assert b[0x40000542-base:0x4000054c-base].hex()=='4ebaff6e41f9fc044000'
assert b[0x400f0504-base:0x400f050e-base].hex()=='2f032f0241f94199dad8'
patches={0x40000542:bytes.fromhex('4ef9')+START.to_bytes(4,'big')+bytes.fromhex('4e714e71'),0x400f0504:bytes.fromhex('4ef9')+DISPATCH.to_bytes(4,'big')+bytes.fromhex('4e714e71')}
s['RANGES'].extend([(BOOT,usedend),(0x40000542,0x40000568),(0x400f0504,0x400f05d6),(0x4009bcb8,0x4009bcc6),(0x40106b6c,0x40106be2)])
s['loop_pcs'].update({CLEAR1+0x20:CLEAR1+0x2c,CLEAR2+0x20:CLEAR2+0x2c})
class Boundary(Exception):pass
class Terminal(Exception):pass
s.update(Boundary=Boundary,Terminal=Terminal)
events=[]
def fetch(pc):
 m=s['active']
 if pc in patches and not (getattr(m,'stock_init',False) and pc==0x400f0504):return patches[pc]
 for a,v in blocks.items():
  if a<=pc<a+len(v):return v[pc-a:pc-a+16]
 if getattr(m,'code_start',0)<=pc<getattr(m,'code_end',0):return bytes(m.read(pc+j,1) for j in range(min(16,m.code_end-pc)))
 return b[pc-base:pc-base+16]
s['placedfetch']=fetch
def observe(m,pc):
 if getattr(m,'code_start',0) and pc==m.code_start+INIT_OFFSET:m.wrapper_status=m.sr
 owner=m.read(0x4199d590,4)
 if owner:
  ready=m.read(owner+0x1410c,4);m.timeline.append((hex(pc),ready))
  if pc in range(0x400f050e,0x400f05d0):
   assert ready==0
   if not getattr(m,'stock_init',False):assert m.sr&0xff00==0x2700
 if pc in [0x400dab8c,0x400ec284]:m.calls.append(pc)
 if pc==0x40000568 or pc==0x4009bcc4:raise Boundary()
 if pc==SPIN or (getattr(m,'code_start',0) and pc==m.code_start+INIT_SPIN_OFFSET):
  m.spin_visits+=1
  if m.spin_visits==3:raise Terminal()
 if pc==0x4000054c:m.map(0xfc044000,4)
s['observe_placed']=observe
src=s['summarysource'].replace('seqfetch(pc)','placedfetch(pc)').replace('range(100000)','range(300000)')
src=src.replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)',"   observe_placed(self,pc)\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
src=src.replace("   elif m=='swap':","   elif m=='movec':self.controls.append((int.from_bytes(i.bytes[2:4],'big')&4095,self.get(ops[0],4)))\n   elif m=='sgt':self.put(ops[0],1,255 if not self.sr&4 and not (bool(self.sr&8)^bool(self.sr&2)) else 0)\n   elif m=='swap':")
exec('if True:\n'+src,s)
checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
def machine():
 m=s['SequenceMachine']();s['active']=m;m.run=s['run'].__get__(m,s['SequenceMachine']);m.summarize=True;m.sr=0x2700;m.controls=[];m.timeline=[];m.calls=[];m.spin_visits=0;m.map(0x30000000,0x4000);m.map(0x401fe590,0x20)
 m.map(TABLE,len(table))
 for j,v in enumerate(table):m.write(TABLE+j,1,v)
 for j in range(0x20):m.write(0x401fe590+j,1,b[0x401fe590-base+j])
 for j,v in enumerate(extension):m.write(stage+j,1,v)
 return m
def startup(m):
 try:m.run(0x40000542)
 except Boundary:pass
 owner=m.read(0x4199d590,4);m.code_start=owner+0x14c80;m.code_end=m.code_start+size;s['RANGES'].append((m.code_start,m.code_end));return owner
check('resident layout fits bounded original interval',usedend<=0x40242000)
check('counted startup table ends before resident layout',0x40241ab8+119*4<=BOOT)
check('original data-copy sources and clear exclude resident layout',usedend<=0x40242000)
for mode in ['cold','reentry','wrong_argument','bad_header','null_owner']:
 m=machine();owner=startup(m);code_before=bytes(m.read(m.code_start+j,1) for j in range(4096));calls_before=len(m.calls)
 check(mode+': actual startup overlay publishes unready allocated owner',owner==0x419a38c0 and m.read(owner+0x1410c,4)==0)
 check(mode+': actual startup replay reaches cache handoff',m.controls==[(2,0xa50ce100),(4,0x4007e020)] and 0x4000054c in m.steps)
 m.reg['a7']=0x30002000;m.sr=0x251b
 baseline=copy.deepcopy(m) if mode=='cold' else None
 if mode=='reentry':
  try:m.run(0x4009bcb8)
  except Boundary:pass
  m.reg['a7']=0x30002000
  m.write(owner+0x14120,4,0x12345678);m.write(owner+0x14c30,4,0x12345678)
 if mode=='bad_header':m.write(owner+0x14104,4,99)
 if mode=='null_owner':m.write(0x4199d590,4,0)
 sp=m.reg['a7'];registers=m.reg.copy();start_steps=len(m.steps);call_count=len(m.calls);terminal=False
 try:
  if mode=='wrong_argument':m.run(0x400f0504,(157,))
  else:m.run(0x4009bcb8)
 except Boundary:pass
 except Terminal:terminal=True
 good=mode in ['cold','reentry']
 check(mode+': initializer outcome',terminal!=good)
 check(mode+': no second allocation',0x400dab8c not in m.calls[call_count:])
 check(mode+': copied code survives initializer',bytes(m.read(m.code_start+j,1) for j in range(4096))==code_before)
 if good:
  check(mode+': complete stock initializer executes both pool loops and owner links',all(pc in m.steps[start_steps:] for pc in [0x400f0516,0x400f0548,0x400f05ac,0x400f05ce]))
  check(mode+': all 64 stock records link correctly',m.read(0x4199fe98,4)==owner and all(m.read(owner+j*0x504+16,4)==(owner+(j+1)*0x504 if j<63 else 0) and m.read(owner+j*0x504,4)==0 for j in range(64)))
  check(mode+': ready published only after stock return',m.read(owner+0x1410c,4)==1 and 0x400f05d4 in m.steps[start_steps:])
  check(mode+': context cleared on init/reentry',all(m.read(owner+0x14120+j,1)==0 for j in range(0xb50)))
  check(mode+': saved wrapper status restored',m.sr==m.wrapper_status and m.sr&0xff00==0x2500)
  check(mode+': callee registers restored',all(m.reg[r]==registers[r] for r in ['d2','d3','d4','d5','d6','d7','a2','a3','a4','a5','a6']))
  # Boundary before caller RTS: its synthetic return word still on stack.
  check(mode+': caller argument balanced',m.reg['a7']==sp-4)
  m.reg['a7']=sp
  if baseline:
   baseline.stock_init=True;s['active']=baseline
   try:baseline.run(0x4009bcb8)
   except Boundary:pass
   check('wrapped initializer matches stock original owner bytes',bytes(m.read(owner+j,1) for j in range(0x14100))==bytes(baseline.read(owner+j,1) for j in range(0x14100)))
   check('wrapped initializer matches stock fixed pool/global bytes',bytes(m.read(0x4199d594+j,1) for j in range(0x2910))==bytes(baseline.read(0x4199d594+j,1) for j in range(0x2910)))
   s['active']=m
  m.reg['d0']=3;m.run(m.code_start+layout['resolve']['offset'])
  check(mode+': ready relocated resolver sees actual initialized owner',m.reg['a0']==owner+0x14c30+48)
 else:
  check(mode+': guard precedes stock mutation',not any(0x400f050e<=pc<0x400f05d6 for pc in m.steps[start_steps:]))
  check(mode+': failure remains masked',m.sr&0xff00==0x2700)
 cases.append({'mode':mode,'owner':hex(owner),'initializer_instructions':len(m.steps)-start_steps,'terminal':terminal,'initializer_calls':m.calls[call_count:],'readiness':m.read(owner+0x1410c,4)})
check('original main unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
check('original SysEx unchanged',hashlib.sha256(pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
result={'checks':checks,'check_count':len(checks),'cases':cases,'resident_blocks':{hex(a):len(v) for a,v in blocks.items()},'resident_end':hex(usedend),'resident_remaining':0x40242000-usedend,'ram_initializer_bytes':len(initcode),'helper_code_bytes':size,'firmware_modified':False,'limits':['Address fetch overlays only; no binary patch/repack.','Bounded interval placement, not global computed-pointer ownership certification.','Application/scheduler path between cache handoff and initializer is not executed; owner/heap survival across that path remains open.','Two recovered call-site overlays tested; complete caller set not certified.','Long clear loops summarized; physical cache coherence remains unverified.','Guard failure is terminal masked spin, not graceful recovery.','Initializer reentry resets proposed contexts; musical semantics of reset require later audit.']}
pathlib.Path('outputs/Digitone-placed-bootstrap-initializer-results.json').write_text(json.dumps(result,indent=2))
lines=[]
for a,v in blocks.items():
 if a==TABLE:continue
 lines.extend(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in h['md'].disasm(v,a))
lines.append('RAM initializer wrapper at cold-allocation destination:')
lines.extend(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in h['md'].disasm(initcode,0x419b8540+INIT_OFFSET))
pathlib.Path('outputs/Digitone-placed-bootstrap-initializer-instructions.txt').write_text('\n'.join(lines))
print('PASS',len(checks),'checks; resident end',hex(usedend),'remaining',0x40242000-usedend)
