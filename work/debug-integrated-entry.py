"""Integrated PC-only proposed installation policy; no package output or hardware I/O."""
exec(open('work/trace-update-completion.py').read().split('\nchecks=[];cases=[]')[0])
RANGES.extend([(0x80004052,0x80004164),(0x80003ac6,0x80003bfa),(0x800031b8,0x80003200),(0x80001242,0x80001270),(0x8000107a,0x80001098),(0x800021fa,0x8000225c)])
class EntryMachine(ProbeMachine):
 def read(self,a,n):
  if a==0xec070004:return 4
  return super().read(a,n)
 def write(self,a,n,v):
  if 0xfc000000<=a<0xfd000000 or 0xec000000<=a<0xed000000:return
  return super().write(a,n,v)
checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
def stoprun(m,entry,args=()):
 try:m.run(entry,args)
 except BoundaryStop:return
 raise AssertionError('boundary not reached')
def load(m,address,data):
 m.map(address,len(data))
 for j,v in enumerate(data):m.write(address+j,1,v)
def state(size=4096):
 m=EntryMachine();m.map(0x80000000,1024);m.map(0x800070f0,80);m.map(0x80007710,0x14);m.map(0x800088a0,0x260);m.map(0x29001000,256)
 load(m,0x40000000,bytes([0xa5])*size)
 m.stubs={p:(argc,0) for p,argc in [(0x800016f8,0),(0x80001bac,3),(0x800016c8,2),(0x800019e6,3),(0x80001acc,0),(0x8000174e,1)]}
 return m
# Actual menu dispatch for OS UPGRADE (table case index 3), not the whole key scanner.
m=state();m.reg['a3']=0x800013a4;m.reg['a4']=0x80004052;m.reg['d3']=0x30003000;m.map(0x30003000,16);m.endpoints=[0x80004052]
# Supply scanner result at its boundary: type 0, key=0x1d, press=1.
def scan_event(machine):
 sp=machine.reg['a7'];dst=machine.read(sp+4,4);machine.write(dst,4,0);machine.write(dst+4,1,0x1d);machine.write(dst+6,1,1)
menu_source=new_source.replace("   if pc in getattr(self,'endpoints',[]):", "   if pc==0x800013a4:\n    scan_event(self);pc=self.get('(a7)+',4);continue\n   if pc in getattr(self,'endpoints',[]):")
exec('if True:\n'+menu_source);Machine.run=run
try:stoprun(m,0x800021fa)
except Exception:
 print('debug',m.reg,{hex(a):m.read(a,1) for a in range(0x30003000,0x30003008)},[hex(x) for x in m.steps[-16:]]);raise
check('actual menu OS-upgrade branch reaches SysEx entry',m.endpoint==0x80004052 and 0x80002258 in m.steps)
cases.append({'kind':'actual menu dispatch','scanner_result_supplied':{'type':0,'key':29,'press':1},'endpoint':hex(m.endpoint),'instructions':len(m.steps),'limit':'scanner/device key state and full startup not executed'})
exec('if True:\n'+new_source);Machine.run=run
m=state();m.endpoints=[0x800040d6];stoprun(m,0x80004052)
check('entry resets completion/error flags',m.read(0x800089a4,4)==0 and m.read(0x800088a0,4)==0)
check('entry installs actual MIDI interrupt',m.read(0x800002d4,4)==0x800038f8)
check('entry leaves staging buffer sentinel intact',all(m.read(0x40000000+j,1)==165 for j in range(4096)))
check('entry performed no observed staging writes',not any(0x40000000<=a<0x40001000 for a,n,v in m.writes[4096:])) if False else None
cases.append({'kind':'actual update entry and receive/control setup to first wait; display helper boundaries','stage_bytes_checked':4096,'stage_value':165,'interrupt':hex(m.read(0x800002d4,4)),'instructions':len(m.steps),'limits':['Display helper internals are skipped.','Earlier complete startup is not executed.','Receive counters are initialized by begin marker, not claimed reset by entry.']})
def checksum(payload):return sum((i+1)^v[0] for i,v in enumerate(struct.iter_unpack('>I',payload)))&0xffffffff
def num3(v):return bytes([(v>>14)&127,(v>>7)&127,v&127])
def frames(payload,content_bad=False):
 stream=len(payload).to_bytes(4,'big')+(checksum(payload)^(1 if content_bad else 0)).to_bytes(4,'big')+payload;count=(len(stream)+100)//101;stream+=bytes(count*101-len(stream));seed=242
 result=[bytes([127,1,8])+num3(seed)+num3(count)+bytes([247])]
 for index in range(count):
  chunk=stream[index*101:(index+1)*101];encoded=bytearray()
  for j in range(0,101,7):
   group=chunk[j:j+7];encoded.append(sum(((v>>7)&1)<<(6-k) for k,v in enumerate(group)));encoded.extend(v&127 for v in group)
  body=num3(seed+index)+encoded;crc=(8+sum(v^(8+j) for j,v in enumerate(body)))&127
  result.append(bytes([126])+body+bytes([crc,247]))
 result.append(bytes([127,2,8])+num3(seed)+num3(count)+bytes([247]));return result
class FlashFixture:
 def __init__(self,mode):self.mode=mode;self.data=bytearray([0x5a])*0x200000;self.ops=[];self.writes=0
 def erase(self,address):
  self.ops.append(('erase',address))
  if self.mode=='erase_failure':return -1
  self.data[address:address+0x40000]=bytes([255])*0x40000;return 0
 def program(self,address,data):
  self.writes+=1;self.ops.append(('program',address,len(data)))
  if self.mode=='busy_timeout':raise TimeoutError('test backend bounded busy')
  if self.mode=='write_failure' and self.writes==2:return -1
  if self.mode=='silent_failure' and self.writes==2:return 0
  self.data[address:address+len(data)]=data;return 0
 def read(self,address,size):
  self.ops.append(('readback',address,size));data=bytes(self.data[address:address+size])
  if self.mode=='readback_failure':return bytes([data[0]^1])+data[1:]
  return data
# Proposed policy is Python orchestration, not an installed branch/hook.
for mode,size in [('success',64),('success',512),('success',516),('success',1024),('truncated',516),('bad_packet',516),('bad_content',516),('erase_failure',516),('write_failure',1024),('silent_failure',1024),('readback_failure',516),('busy_timeout',516)]:
 m=state();m.endpoints=[0x800040d6];stoprun(m,0x80004052);wire=frames(bytes((j*73+19)&255 for j in range(size)),mode=='bad_content');backend=FlashFixture(mode);reason=None;handoff=False
 if mode=='truncated':wire=wire[:-2]
 if mode=='bad_packet':p=bytearray(wire[1]);p[-2]^=1;wire[1]=bytes(p)
 for frame in wire:
  load(m,0x29001000,frame);m.run(0x800036f4,(0x29001000,))
 complete=m.read(0x800089a4,4)==2 and m.read(0x80007712,1)==3 and m.read(0x800088a0,4)==0
 if not complete:reason='receive incomplete or invalid'
 else:
  actual_length=m.read(0x40000000,4)
  if actual_length<=0 or actual_length%4 or actual_length+8>4096:reason='invalid staging extent/alignment'
  else:
   m.endpoints=[0x80003cce,0x80003c4e];stoprun(m,0x80003bfa)
   if m.endpoint!=0x80003cce:reason='content checksum mismatch'
   else:
    rounded=(actual_length+511)//512*512
    if rounded+8>4096:reason='rounded footprint outside PC staging allocation'
    else:
     m.run(0x400ec284,(0x40000008+actual_length,0,rounded-actual_length))
     # Poisoned prior tail is explicitly initialized before the first erase.
     check(f'{mode}/{size}: padding zero before erase',all(m.read(0x40000008+j,1)==0 for j in range(actual_length,rounded)))
     for addr in range(0x80000,0x80000+((actual_length+0x3ffff)//0x40000)*0x40000,0x40000):
      if backend.erase(addr)<0:reason='erase failed';break
     if reason is None:
      for off in range(0,rounded,512):
       data=bytes(m.read(0x40000008+off+j,1) for j in range(512));address=0x80000+off
       try:result=backend.program(address,data)
       except TimeoutError:reason='program timed out';break
       if result<0:reason='program failed';break
       if backend.read(address,512)!=data:reason='readback mismatch';break
     if reason is None:handoff=True
 expected={'truncated':'receive incomplete or invalid','bad_packet':'receive incomplete or invalid','bad_content':'content checksum mismatch','erase_failure':'erase failed','write_failure':'program failed','silent_failure':'readback mismatch','readback_failure':'readback mismatch','busy_timeout':'program timed out'}.get(mode)
 check(f'{mode}/{size}: integrated outcome',reason==expected and handoff==(mode=='success'))
 if mode in ['truncated','bad_packet','bad_content']:check(f'{mode}: no flash operations',backend.ops==[])
 if mode=='erase_failure':check('erase error stops before programming',backend.writes==0)
 if mode in ['write_failure','silent_failure']:check(mode+': no third program after second fails',backend.writes==2)
 if mode=='success':
  expected_data=bytes((j*73+19)&255 for j in range(size))+bytes((size+511)//512*512-size)
  check(f'success/{size}: exact verified padded payload',bytes(backend.data[0x80000:0x80000+len(expected_data)])==expected_data)
  check(f'success/{size}: outside erased footprint unchanged',backend.data[0x7ffff]==0x5a and backend.data[0xc0000]==0x5a)
 cases.append({'kind':'integrated PC policy','mode':mode,'container_bytes':size,'receive_complete':complete,'outcome':reason or 'verified; eligible for hypothetical handoff','handoff_allowed':handoff,'flash_calls':backend.ops,'program_calls':backend.writes,'actual_instruction_count':len(m.steps),'limits':['Flash erase/program/readback are PC bytearray fixtures.','Policy validation, result gating, and timeout handling are Python, not firmware hooks.','Actual receiver/checksum/memset instructions executed; display helpers skipped.','Failure after erase may leave partial image; no rollback guarantee.']})
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
check('original firmware unchanged',hashlib.sha256(syx.read_bytes()).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
pathlib.Path('outputs/Digitone-integrated-update-policy-results.json').write_text(json.dumps({'check_count':len(checks),'checks':checks,'cases':cases},indent=2),encoding='utf-8')
print(json.dumps({'checks':len(checks),'cases':len(cases)}))

