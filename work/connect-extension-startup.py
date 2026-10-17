"""PC-only connection of verified helper bytes to allocated startup RAM.
No compressed main, container, binary artifact, or installed hook is generated.
"""
import pathlib, hashlib, json

def definitions(path, marker):
 ns={};exec(pathlib.Path(path).read_text().split(marker)[0],ns);return ns

h=definitions('work/test-actual-capture-and-pitch.py','\nchecks=[];cases=[];OWNER=')
s=definitions('work/execute-proposed-startup-sequence.py','\nchecks=[];cases=[]')
u=definitions('work/test-integrated-update-policy.py','\nchecks=[];cases=[]')
utext=pathlib.Path('work/test-integrated-update-policy.py').read_text()
exec(utext[utext.index('def stoprun('):utext.index('# Actual menu dispatch')],u)
exec(utext[utext.index('def checksum('):utext.index('# Proposed policy')],u)
checks=[];cases=[]
def check(name,ok):
 assert ok,name
 checks.append(name)

# Pack tested bodies without altering their instruction bytes. Absolute fixups
# are applied only after the real allocator determines the destination.
layout={};offset=0
for name,old in h['names'].items():
 code=h['fixtures'][old];layout[name]={'old':old,'offset':offset,'size':len(code)};offset+=len(code)
check('tested helper bodies fit 4096-byte reserve',offset==1678 and offset<=4096)
extension=bytearray(4096)
for name,item in layout.items():extension[item['offset']:item['offset']+item['size']]=h['fixtures'][item['old']]
extension=bytes(extension);extension_hash=hashlib.sha256(extension).hexdigest()

def verified_receive(mode):
 # Extension unit fixture, not an Elektron container or a main-image depack.
 m=u['state']();m.endpoints=[0x800040d6];u['stoprun'](m,0x80004052)
 wire=u['frames'](extension,mode=='bad_content')
 if mode=='truncated':wire=wire[:-2]
 fresh=False
 for frame in wire:
  u['load'](m,0x29001000,frame);m.run(0x800036f4,(0x29001000,))
  if frame[:3]==bytes([127,1,8]) and m.read(0x80007712,1)==1 and m.read(0x8000771c,4)==0:fresh=True
 if not(fresh and m.read(0x80007712,1)==3 and m.read(0x800089a4,4)==2 and m.read(0x800088a0,4)==0):return None
 m.endpoints=[0x80003cce,0x80003c4e];u['stoprun'](m,0x80003bfa)
 if m.endpoint!=0x80003cce:return None
 backend=u['FlashFixture']('silent_failure' if mode=='silent_failure' else 'success')
 assert backend.erase(0x80000)==0
 for off in range(0,4096,512):
  data=bytes(m.read(0x40000008+off+j,1) for j in range(512))
  if backend.program(0x80000+off,data)<0 or backend.read(0x80000+off,512)!=data:return None
 return bytes(backend.data[0x80000:0x81000])

verified=verified_receive('success')
check('receiver checksum and PC readback preserve exact helper extension',verified==extension)
for mode in ['truncated','bad_content','silent_failure']:
 check(mode+' cannot provide startup bytes',verified_receive(mode) is None)

class HandoffStop(Exception):pass
s['HandoffStop']=HandoffStop
s['RANGES'].extend([(0x40000554,0x40000568),(0x40106b6c,0x40106be2)])
def ramfetch(pc):
 m=s['active']
 if getattr(m,'code_start',0)<=pc<getattr(m,'code_end',0):return bytes(m.read(pc+j,1) for j in range(min(16,m.code_end-pc)))
 return s['seqfetch'](pc)
s['ramfetch']=ramfetch
src=s['summarysource'].replace('seqfetch(pc)','ramfetch(pc)')
src=src.replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)',"   if pc==0x40000568:raise HandoffStop()\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
src=src.replace("   elif m=='swap':","   elif m=='movec':\n    self.controls.append({'pc':hex(pc),'selector':int.from_bytes(i.bytes[2:4],'big')&4095,'value':self.get(ops[0],4)})\n   elif m=='sgt':self.put(ops[0],1,255 if not self.sr&4 and not (bool(self.sr&8)^bool(self.sr&2)) else 0)\n   elif m=='swap':")
exec('if True:\n'+src,s)

relocations=[]
def relocate(dest):
 result=bytearray(extension)
 for name,item in layout.items():
  code=h['fixtures'][item['old']]
  for ins in h['md'].disasm(code,item['old']):
   # Every known cross-body reference is an absolute long address operand.
   for olditem in layout.values():
    target=olditem['old']
    if not (f'${target:x}' in ins.op_str):continue
    literal=target.to_bytes(4,'big');pos=bytes(ins.bytes).find(literal)
    if pos<0:continue
    at=item['offset']+ins.address-item['old']+pos
    replacement=dest+olditem['offset'];result[at:at+4]=replacement.to_bytes(4,'big')
    relocations.append({'body':name,'offset':at,'old':hex(target),'new':hex(replacement)})
  # The event allocation trampoline PEA targets an interior return boundary.
  if name=='allocate_clear':
   target=int.from_bytes(code[2:6],'big');assert target==item['old']+18
   at=item['offset']+2;result[at:at+4]=(dest+item['offset']+18).to_bytes(4,'big')
   relocations.append({'body':name,'offset':at,'old':hex(target),'new':hex(dest+item['offset']+18)})
 return bytes(result)

for mode in ['cold','warm','exhausted','corrupt_stage']:
 m=s['SequenceMachine']();s['active']=m;m.run=s['run'].__get__(m,s['SequenceMachine']);m.summarize=True;m.controls=[];m.sr=0x2700;m.map(0x30000000,0x4000);m.map(0x401fe590,0x20)
 for j in range(0x20):m.write(0x401fe590+j,1,s['b'][0x401fe590-s['base']+j])
 # Explicit bridge: verified unit bytes supplied at the decoded extension
 # destination. Full extended-container read/depack is not claimed here.
 stage=s['stage']
 for j,v in enumerate(verified):m.write(stage+j,1,v)
 if mode=='corrupt_stage':m.write(stage+101,1,m.read(stage+101,1)^1)
 m.run(0x50030000);m.run(0x50030100)
 check(mode+': split clear preserves stage',bytes(m.read(stage+j,1) for j in range(4096))==(verified if mode!='corrupt_stage' else verified[:101]+bytes([verified[101]^1])+verified[102:]))
 if mode=='warm':m.run(0x400dab8c,(0x15c80,))
 if mode=='exhausted':check('actual allocator exhausts heap',m.run(0x400dab8c,(0x1000000,))==s['heaplo'])
 good=hashlib.sha256(bytes(m.read(stage+j,1) for j in range(4096))).hexdigest()==extension_hash
 owner=m.run(0x400dab8c,(0x15c80,)) if good else 0
 destination=owner+0x14c80 if owner else None
 if owner:
  m.run(0x400ec284,(owner,0,0x15c80));m.run(0x400ec23c,(destination,stage,4096))
  check(mode+': exact copied helper bytes before relocation',bytes(m.read(destination+j,1) for j in range(4096))==verified)
  patched=relocate(destination)
  # PC relocation stores, not yet a machine-code relocation/bootstrap helper.
  for j,v in enumerate(patched):m.write(destination+j,1,v)
  check(mode+': code reserve tail stays zero',all(m.read(destination+j,1)==0 for j in range(offset,4096)))
 m.run(0x400ec284,(stage,0,4096))
 check(mode+': source erased and owner unpublished',all(m.read(stage+j,1)==0 for j in range(4096)) and m.read(0x4199d590,4)==0)
 check(mode+': allocator and copy run before cache controls',m.controls==[])
 if owner:
  m.code_start=destination;m.code_end=destination+offset;s['RANGES'].append((m.code_start,m.code_end))
  sp=m.reg['a7']
  try:m.run(0x40000554)
  except HandoffStop:pass
  else:raise AssertionError('handoff boundary missed')
  m.reg['a7']=sp # Boundary is before application call; discard test return frame.
  check(mode+': actual cache-control order',[(x['selector'],x['value']) for x in m.controls]==[(2,0xa50ce100),(4,0x4007e020)])
  check(mode+': cache handoff does not alter copied code',bytes(m.read(destination+j,1) for j in range(4096))==patched)
  addr=lambda name:destination+layout[name]['offset']
  # Isolated publication/header fixture AFTER cache handoff, not full init.
  m.reg['d0']=0;m.run(addr('resolve'))
  check(mode+': relocated resolver rejects unpublished owner',m.reg['a0']==0)
  m.write(0x4199d590,4,owner)
  for off,v in [(0,0x534c4332),(4,2),(8,0xb70)]:m.write(owner+0x14100+off,4,v)
  m.reg['d0']=0;m.run(addr('resolve'))
  check(mode+': resolver rejects unready header',m.reg['a0']==0)
  m.write(owner+0x1410c,4,1);m.reg['d0']=2;m.run(addr('resolve'))
  check(mode+': relocated resolver returns owned track record',m.reg['a0']==owner+0x14c30+32)
  word=0x80000000|60|(1<<7)
  check(mode+': relocated quantizer calls stock scale membership',m.run(addr('quantize'),(61,word))==60)
  check(mode+': masked supervisor state preserved',m.sr&0xff00==0x2700)
 else:
  check(mode+': failure stays unready without cache/application handoff',m.read(0x4199d590,4)==0 and m.controls==[])
 cases.append({'mode':mode,'owner':hex(owner),'code_destination':None if destination is None else hex(destination),'instruction_count':len(m.steps),'cache_controls':m.controls,'handoff':'stock cache register writes only; application entry not executed' if owner else 'blocked by proposed PC policy','clear_summaries':m.summaries})

check('decoded main unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
check('original SysEx unchanged',hashlib.sha256(pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
result={'check_count':len(checks),'checks':checks,'cases':cases,'helper_bytes':offset,'reserve_bytes':4096,'extension_sha256':extension_hash,'layout':layout,'relocations':relocations,'firmware_modified':False,'limits':['Extension receive is a unit fixture, not a complete extended firmware container.','Decoded extension placement is an explicit PC bridge; actual extended-main read/depack has not been integrated.','Split-clear routines are RAM fixtures and large loops use previously validated summaries.','Relocation and failure gating are Python; no installed bootstrap.','Only resolver and quantizer executed at allocated address; all relocated helpers not yet audited.','MOVEC register writes recorded; physical instruction/data caches, coherency and inherited loader cache state not simulated.','Publication/readiness header supplied for isolated helper checks; full stock initializer and application entry not run.','Null/corruption paths block the PC handoff, not a verified stock fallback.']}
pathlib.Path('outputs/Digitone-extension-startup-connection-results.json').write_text(json.dumps(result,indent=2))
print('PASS',len(checks),'checks;',len(cases),'startup cases;',offset,'helper bytes')
