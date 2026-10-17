"""Machine-code bootstrap fixture only. No firmware patch or binary output."""
import pathlib,json,hashlib
c={};exec(pathlib.Path('work/connect-extension-startup.py').read_text().split('\nverified=verified_receive')[0],c)
h,s=c['h'],c['s'];extension=c['extension'];layout=c['layout'];size=c['offset'];stage=s['stage']
prior=json.loads(pathlib.Path('outputs/Digitone-extension-startup-connection-results.json').read_text())
assert hashlib.sha256(extension).hexdigest()==prior['extension_sha256']
entries={}
for r in prior['relocations']:
 entries.setdefault(r['offset'],(int(r['old'],16),int(r['new'],16)-0x419b8540))
assert len(entries)==18
assert all(0<=off<=size-4 and 0<=target<size for off,(_,target) in entries.items())
table=b''.join(off.to_bytes(4,'big')+old.to_bytes(4,'big')+target.to_bytes(4,'big') for off,(old,target) in sorted(entries.items()))
ENTRY=0x50040000;TABLE=0x50041000
a=h['Asm']();absolute=h['absolute'];h['save'](a)
# SR is preserved by save; keep all setup work masked.
a.emit('46fc2700');absolute(a,'4eb9',0x50030000);absolute(a,'4eb9',0x50030100)
# Sum the complete preserved reserve, comparing a compile-time fixture value.
a.emit('207c'+stage.to_bytes(4,'big').hex()+'4281243c00001000')
a.label('sum');a.emit('42801018d2805382');a.branch('6600','sum')
a.emit('0c81'+(sum(extension)&0xffffffff).to_bytes(4,'big').hex());a.branch('6600','failure')
a.emit('2f3c00015c80');absolute(a,'4eb9',0x400dab8c);a.emit('588f2400');a.branch('6700','failure')
a.emit('2f3c00015c8042a72f02');absolute(a,'4eb9',0x400ec284);a.emit('4fef000c2642d7fc00014c80')
a.emit('2f3c000010002f3c'+stage.to_bytes(4,'big').hex()+'2f0b');absolute(a,'4eb9',0x400ec23c);a.emit('4fef000c')
VALIDATE=ENTRY+len(a.code)
# Independently checksum the actual destination before trusting copied code.
a.emit('204b4281243c00001000');a.label('copy_sum');a.emit('42801018d2805382');a.branch('6600','copy_sum')
a.emit('0c81'+(sum(extension)&0xffffffff).to_bytes(4,'big').hex());a.branch('6600','failure')
# The checksum uses d2; recover the owner from the code base, whose offset
# within the allocation is fixed.
a.emit('240b048200014c80')
# Check every table record before writing any relocated operand.
a.emit('287c'+TABLE.to_bytes(4,'big').hex()+'263c'+len(entries).to_bytes(4,'big').hex())
a.label('validate');a.emit('201c221c281c0c80'+(size-4).to_bytes(4,'big').hex());a.branch('6200','failure')
a.emit('08000000');a.branch('6600','failure');a.emit('0c84'+(size-1).to_bytes(4,'big').hex());a.branch('6200','failure')
a.emit('08040000');a.branch('6600','failure');a.emit('204bd1c0b290');a.branch('6600','failure');a.emit('5383');a.branch('6600','validate')
a.emit('287c'+TABLE.to_bytes(4,'big').hex()+'263c'+len(entries).to_bytes(4,'big').hex())
a.label('relocate');a.emit('201c588c281c204bd1c0220bd28420815383');a.branch('6600','relocate')
# Header exists but stays unready and unpublished. Application initializer still
# has to finish its stock work; this bootstrap does not perform that work.
a.emit('2042d1fc0001410020bc534c4332217c000000020004217c00000b700008')
a.emit('2f3c0000100042a72f3c'+stage.to_bytes(4,'big').hex());absolute(a,'4eb9',0x400ec284);a.emit('4fef000c2f420000');h['restore'](a);a.emit('4e75')
a.label('failure');a.emit('2f3c0000100042a72f3c'+stage.to_bytes(4,'big').hex());absolute(a,'4eb9',0x400ec284);a.emit('4fef000c46fc2700')
a.label('spin');a.emit('60fe')
code=a.done();SPIN=ENTRY+a.labels['spin']
instructions=[f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in h['md'].disasm(code,ENTRY)]
assert sum(i.size for i in h['md'].disasm(code,ENTRY))==len(code)
s['fixtures'][ENTRY]=code;s['RANGES'].append((ENTRY,ENTRY+len(code)))
class SpinStop(Exception):pass
class CacheStop(Exception):pass
s.update(SpinStop=SpinStop,CacheStop=CacheStop)
def fetch(pc):
 m=s['active']
 if getattr(m,'code_start',0)<=pc<getattr(m,'code_end',0):return bytes(m.read(pc+j,1) for j in range(min(16,m.code_end-pc)))
 return s['seqfetch'](pc)
s['bootfetch']=fetch
src=s['summarysource'].replace('seqfetch(pc)','bootfetch(pc)')
src=src.replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)',f"   if pc=={SPIN}:\n    self.spin_visits+=1\n    if self.spin_visits==3:raise SpinStop()\n   if pc==0x40000568:raise CacheStop()\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
src=src.replace('   self.steps.append(pc)',f"   self.steps.append(pc)\n   if pc=={VALIDATE} and self.corrupt_copy:\n    self.corrupt_copy=False;self.write(self.reg['a3']+self.corrupt_offset,1,self.read(self.reg['a3']+self.corrupt_offset,1)^1)")
src=src.replace("   elif m=='swap':","   elif m=='movec':self.controls.append((int.from_bytes(i.bytes[2:4],'big')&4095,self.get(ops[0],4)))\n   elif m=='sgt':self.put(ops[0],1,255 if not self.sr&4 and not (bool(self.sr&8)^bool(self.sr&2)) else 0)\n   elif m=='swap':")
exec('if True:\n'+src,s)
s['RANGES'].extend([(0x40000554,0x40000568),(0x40106b6c,0x40106be2)])
checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
for mode in ['cold','warm','exhausted','bad_source','bad_copy','bad_copy_nonoperand','offset_outside','target_outside','odd_offset','wrong_expected']:
 m=s['SequenceMachine']();s['active']=m;m.run=s['run'].__get__(m,s['SequenceMachine']);m.summarize=True;m.spin_visits=0;m.corrupt_copy=mode in ['bad_copy','bad_copy_nonoperand'];m.corrupt_offset=min(entries) if mode=='bad_copy' else 0;m.controls=[];m.sr=0x2700;m.map(0x30000000,0x4000);m.map(0x401fe590,0x20);m.map(TABLE,len(table))
 for j,v in enumerate(table):m.write(TABLE+j,1,v)
 if mode=='offset_outside':m.write(TABLE,4,4096)
 if mode=='target_outside':m.write(TABLE+8,4,4096)
 if mode=='odd_offset':m.write(TABLE,4,1)
 if mode=='wrong_expected':m.write(TABLE+4,4,0)
 for j in range(0x20):m.write(0x401fe590+j,1,s['b'][0x401fe590-s['base']+j])
 for j,v in enumerate(extension):m.write(stage+j,1,v)
 if mode=='bad_source':m.write(stage+101,1,m.read(stage+101,1)^1)
 # Pressure allocations are performed after preclear, then bootstrap itself
 # executes the same clears again. Allocator heap survives only outside clear
 # in the stock layout? To avoid silently wiping heap setup, inject pressure at
 # the allocator boundary using actual allocations before bootstrap request.
 m.pressure_mode=mode
 pressure_pc=next(i.address for i in h['md'].disasm(code,ENTRY) if i.mnemonic=='jsr' and '$400dab8c' in i.op_str)
 # Separate entry variant: prefill allocator immediately after checksum by an
 # actual nested run, with interpreter registers/flags restored at boundary.
 def pressure(machine):
  if machine.pressure_mode not in ['warm','exhausted']:return
  saved=machine.reg.copy();sr=machine.sr;machine.pressure_mode=None
  machine.run(0x400dab8c,(0x15c80 if mode=='warm' else 0x1000000,));machine.reg=saved;machine.sr=sr
 s['pressure']=pressure
 testsrc=src.replace('   self.steps.append(pc)',f'   if pc=={pressure_pc}:pressure(self)\n   self.steps.append(pc)')
 exec('if True:\n'+testsrc,s);m.run=s['run'].__get__(m,s['SequenceMachine'])
 initial=m.reg.copy();spin=False
 try:owner=m.run(ENTRY)
 except SpinStop:owner=0;spin=True
 success=mode in ['cold','warm']
 check(mode+': machine outcome',spin!=success and bool(owner)==success)
 check(mode+': source erased',all(m.read(stage+j,1)==0 for j in range(4096)))
 check(mode+': owner never published',m.read(0x4199d590,4)==0)
 check(mode+': no cache or scheduler handoff during bootstrap',not m.controls and not any(pc in m.steps for pc in [0x40001a9e,0x40001bcc,0x40000554]))
 if success:
  dest=owner+0x14c80;m.code_start=dest;m.code_end=dest+size;s['RANGES'].append((dest,dest+size))
  expected=bytearray(extension)
  for off,(old,target) in entries.items():expected[off:off+4]=(dest+target).to_bytes(4,'big')
  check(mode+': actual relocation equals independent byte oracle',bytes(m.read(dest+j,1) for j in range(4096))==expected)
  check(mode+': bootstrap restores stack and callee registers',m.reg['a7']==initial['a7'] and all(m.reg[r]==initial[r] for r in ['d2','d3','d4','d5','d6','d7','a2','a3','a4','a5','a6']))
  check(mode+': initialized metadata remains unready',m.read(owner+0x14100,4)==0x534c4332 and m.read(owner+0x14104,4)==2 and m.read(owner+0x14108,4)==0xb70 and m.read(owner+0x1410c,4)==0)
  sp=m.reg['a7']
  try:m.run(0x40000554)
  except CacheStop:pass
  m.reg['a7']=sp
  check(mode+': stock cache writes occur after bootstrap return',m.controls==[(2,0xa50ce100),(4,0x4007e020)])
  check(mode+': relocated quantizer executes',m.run(dest+layout['quantize']['offset'],(61,0x800000bc))==60)
 else:
  check(mode+': failure is a real masked self-loop',m.spin_visits==3 and m.sr&0xff00==0x2700)
  check(mode+': failure never returns to caller',m.reg['a7']!=initial['a7'])
  if s['heaplo']<=m.reg['a3']<s['heaphi']:
   expected=bytearray(extension)
   if mode in ['bad_copy','bad_copy_nonoperand']:expected[m.corrupt_offset]^=1
   check(mode+': failure makes no relocation writes',bytes(m.read(m.reg['a3']+j,1) for j in range(4096))==expected)
 cases.append({'mode':mode,'owner':hex(owner),'machine_instructions':len(m.steps),'spin_visits':m.spin_visits,'cache_controls':m.controls})
check('original decoded main unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
check('original SysEx unchanged',hashlib.sha256(pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
result={'check_count':len(checks),'checks':checks,'cases':cases,'bootstrap_bytes':len(code),'relocation_table_bytes':len(table),'relocation_count':len(entries),'fixture_address':hex(ENTRY),'failure_spin':hex(SPIN),'firmware_modified':False,'limits':['Synthetic executable placement; physical ownership and installed call site not established.','Failure is a proposed mask-and-spin terminal path, not graceful stock fallback/recovery.','Stage checksum is additive corruption detection, not authentication.','Allocator pressure supplied by actual nested stock allocation at a controlled boundary.','Large clear loops summarized; physical cache coherence not modeled.','Stock application entry and complete initializer not executed; ownership publication deliberately absent.','Full firmware container/read/depack integration remains separate.']}
pathlib.Path('outputs/Digitone-machine-bootstrap-results.json').write_text(json.dumps(result,indent=2))
pathlib.Path('outputs/Digitone-machine-bootstrap-instructions.txt').write_text('\n'.join(instructions))
print('PASS',len(checks),'checks;',len(code),'bootstrap bytes;',len(entries),'relocations')
