"""Read-only receiver, checksum, padding, and failure probes."""
exec(open('work/trace-section-descriptor-storage.py').read().split('checks=[];cases=[]')[0])
import struct
RANGES.extend([(0x80003686,0x800038f8),(0x80003bfa,0x80003cce),(0x80003f6a,0x80003fd8),(0x400d9e26,0x400da0a8),(0x400edb42,0x400edc28),(0x400ecf7a,0x400ed0bc),(0x400ed272,0x400ed2f4),(0x4008ad76,0x4008ad9c),(0x4008ae3c,0x4008aec4)])
class BoundaryStop(Exception):pass
new_source=run_source.replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)', '''   if pc in getattr(self,'endpoints',[]):self.endpoint=pc;raise BoundaryStop()
   if pc in getattr(self,'stubs',{}):
    sp=self.reg['a7'];argc,result=self.stubs[pc];argv=[self.read(sp+4+j*4,4) for j in range(argc)];self.calls.append((pc,argv))
    if pc==0x40001cda:self.delivered.append(argv[1])
    if pc==0x400ec5a8:result=self.status.pop(0) if self.status else self.status_default
    if pc==0x400ec5a8 and getattr(self,'poll_limit',0) and sum(callpc==pc for callpc,_ in self.calls)>=self.poll_limit:self.endpoint=pc;raise BoundaryStop()
    self.reg['d0']=result&0xffffffff;pc=self.get('(a7)+',4);continue
   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)''').replace("   elif m=='nop':pass","   elif m in ('nop','tpf'):pass")
exec('if True:\n'+new_source);Machine.run=run
class ProbeMachine(StorageMachine):
 def __init__(self):
  super().__init__(table());self.stubs={};self.calls=[];self.delivered=[];self.endpoints=[];self.status=[];self.status_default=0
 def ea(self,s,n=4):
  match=re.fullmatch(r'\$([0-9a-f]+)\(pc, ([da][0-7])\.l(?: \* ([1248]))?\)',s)
  if match:return (int(match[1],16)+self.reg[match[2]]*int(match[3] or 1))&0xffffffff
  return super().ea(s,n)
 def write(self,a,n,v):
  if a==0xfc04c01c:return
  return super().write(a,n,v)
checks=[];cases=[]
def check(name,condition):assert condition,name;checks.append(name)
def stoprun(m,entry,args=()):
 try:m.run(entry,args)
 except BoundaryStop:return
 raise AssertionError('boundary not reached')
def load(m,address,data):
 m.map(address,len(data))
 for j,v in enumerate(data):m.write(address+j,1,v)
# Decode the supplied original only, with no files written.
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx').read_bytes();msgs=[];pos=0
while pos<len(syx):
 end=syx.index(247,pos+1);msgs.append(syx[pos+1:end]);pos=end+1
packets=[p for p in msgs if p[5]==126];markers=[p for p in msgs if p[5]==127];decoded=bytearray()
for packet in packets:
 for k in range(9,125,8):
  tag=packet[k]
  decoded.extend(v|(((tag>>(6-j))&1)<<7) for j,v in enumerate(packet[k+1:min(k+8,125)]))
length,stored=struct.unpack('>II',decoded[:8]);container=bytes(decoded[8:8+length]);pad=bytes(decoded[8+length:])
check('stock packet checksums',all(((markers[0][7]+sum(p[6+j]^(markers[0][7]+j) for j in range(119)))&127)==p[125] for p in packets))
check('stock full content checksum',sum((j+1)^v[0] for j,v in enumerate(struct.iter_unpack('>I',container)))&0xffffffff==stored)
check('stock wire padding',len(pad)==72 and not any(pad))
# Actual bootstrap marker/packet handler; mutation scenarios are RAM fixtures only.
for scenario in ['first_packet','bad_checksum','wrong_sequence','bad_terminator','early_end','valid_end','bad_end_seed','bad_end_count']:
 m=ProbeMachine();m.map(0x80007710,0x14);m.map(0x800088a0,0x260);m.map(0x40000000,512);m.map(0x29001000,256)
 def feed(packet):
  payload=packet[5:]+bytes([247]);load(m,0x29001000,payload);m.run(0x800036f4,(0x29001000,))
 feed(markers[0]);check(scenario+': begin enters receiving state',m.read(0x80007712,1)==1 and m.read(0x8000771c,4)==0)
 if scenario in ['first_packet','bad_checksum','wrong_sequence','bad_terminator']:
  p=bytearray(packets[0])
  if scenario=='bad_checksum':p[125]^=1
  if scenario=='wrong_sequence':p[8]^=1
  if scenario=='bad_terminator':
   payload=bytes(p[5:])+bytes([246]);load(m,0x29001000,payload);m.run(0x800036f4,(0x29001000,))
  else:feed(p)
  if scenario=='first_packet':
   check('first valid packet decoded exactly',bytes(m.read(0x40000000+j,1) for j in range(101))==decoded[:101])
   check('first valid packet advances counters',m.read(0x8000771c,4)==1 and m.read(0x80007712,1)==1)
  elif scenario=='bad_terminator':check('bad packet terminator is ignored',m.read(0x8000771c,4)==0)
  else:check(scenario+': invalidates receiving state',m.read(0x80007712,1)==0 and m.read(0x800088a0,4)==1)
 else:
  end=bytearray(markers[1])
  if scenario!='early_end':
   m.write(0x80007712,1,2);m.write(0x8000771c,4,len(packets))
  if scenario=='bad_end_seed':end[7]^=1
  if scenario=='bad_end_count':end[13]^=1
  feed(end)
  if scenario=='valid_end':check('valid end publishes completion',m.read(0x800089a4,4)==2 and m.read(0x80007712,1)==3)
  else:check(scenario+': no successful completion',m.read(0x800089a4,4)!=2)
 cases.append({'kind':'actual bootstrap SysEx handler','scenario':scenario,'state':m.read(0x80007712,1),'received_packets':m.read(0x8000771c,4),'error_flag':m.read(0x800088a0,4),'completion':m.read(0x800089a4,4),'instructions':len(m.steps),'limit':'valid-end case supplies prior completed counter/state; full 10912-packet execution not performed'})
# Execute the actual final two SysEx packets and end marker from a validated-prefix fixture.
m=ProbeMachine();m.map(0x80007710,0x14);m.map(0x800088a0,0x260);m.map(0x29001000,256)
def feed_tail(packet):
 load(m,0x29001000,packet[5:]+bytes([247]));m.run(0x800036f4,(0x29001000,))
feed_tail(markers[0]);prefix_count=len(packets)-2
m.write(0x8000771c,4,prefix_count);m.write(0x80007720,4,((packets[-2][6]<<14)|(packets[-2][7]<<7)|packets[-2][8]))
start=0x40000000+prefix_count*101;m.map(start,202+512)
for j in range(202+512):m.write(start+j,1,0xa5)
feed_tail(packets[-2]);check('penultimate actual packet remains receiving',m.read(0x80007712,1)==1)
feed_tail(packets[-1]);check('last actual packet changes to end-wait state',m.read(0x80007712,1)==2 and m.read(0x8000771c,4)==len(packets))
check('actual final two packets decode exact tail',bytes(m.read(start+j,1) for j in range(202))==decoded[-202:])
feed_tail(markers[1]);check('actual final packet/end chain completes',m.read(0x800089a4,4)==2 and m.read(0x80007712,1)==3)
check('actual final receive leaves unreceived tail untouched',all(m.read(start+202+j,1)==0xa5 for j in range(232)))
cases.append({'kind':'actual final two stock SysEx packets and end marker','prefix_packets_supplied_as_verified_state':prefix_count,'completion':m.read(0x800089a4,4),'wire_zero_padding':72,'unreceived_tail_sentinel':165,'instructions':len(m.steps),'limitation':'prefix count/state supplied; not a full uninterrupted hardware receive session'})
# A bad checksum can still decode the packet, but does not authorize completion.
m=ProbeMachine();m.map(0x80007710,0x14);m.map(0x800088a0,0x260);m.map(0x40000000,256);m.map(0x29001000,256)
def feed_bad_chain(packet):
 load(m,0x29001000,packet[5:]+bytes([247]));m.run(0x800036f4,(0x29001000,))
feed_bad_chain(markers[0]);bad=bytearray(packets[0]);bad[125]^=1;feed_bad_chain(bad);feed_bad_chain(markers[1])
check('bad-checksum packet followed by end cannot complete',m.read(0x800089a4,4)!=2 and m.read(0x80007712,1)==0)
cases.append({'kind':'actual bad-checksum packet then end chain','received_counter':m.read(0x8000771c,4),'completion':m.read(0x800089a4,4),'error_flag':m.read(0x800088a0,4),'instructions':len(m.steps),'observation':'invalid packet is decoded and counter advances, but receiving state is invalidated'})
# Full binary receiver with chunk splitting. Notification is a recorded boundary.
for scenario,chunks,alter,truncated in [('whole',[1000],False,False),('single_bytes',[1]*40,False,False),('split',[2,1,5,3,7,1000],False,False),('altered_payload',[1000],True,False),('truncated',[1000],False,True)]:
 m=ProbeMachine();m.map(0x41924400,0x4a0);m.map(0x401fe564,8);load(m,0x29002000,bytes([165])*128);m.stubs[0x40001cda]=(2,0)
 m.run(0x400d9e26,(128,0x29002000));m.write(0x401fe568,4,0x12345678)
 payload=bytearray(range(32));payload[7]^=1 if alter else 0;stream=bytes([0x21])+len(payload).to_bytes(4,'big')+payload
 if truncated:stream=stream[:-1]
 offset=0
 for take in chunks:
  part=stream[offset:offset+take]
  if not part:break
  load(m,0x29001000,part);m.run(0x400d9e3c,(0x29001000,len(part)));offset+=len(part)
 check(scenario+': completion only after full declared payload',len(m.delivered)==(0 if truncated else 1))
 check(scenario+': exact payload copy',bytes(m.read(0x29002008+j,1) for j in range(len(payload)-(1 if truncated else 0)))==payload[:len(payload)-(1 if truncated else 0)])
 check(scenario+': tail beyond payload unchanged',m.read(0x29002028,1)==165)
 cases.append({'kind':'actual binary receiving function with actual copy helper and notification boundary','scenario':scenario,'bytes_fed':offset,'notifications':len(m.delivered),'receiver_state':m.read(0x41924410,4),'tail_byte':m.read(0x29002028,1),'instructions':len(m.steps)})
# Actual bootstrap checksum loop and branch, small full fixtures.
for count,corrupt in [(4,False),(64,False),(64,True),(65,False)]:
 payload=bytes((j*73+19)&255 for j in range(count));expected=sum((j+1)^v[0] for j,v in enumerate(struct.iter_unpack('>I',payload[:len(payload)//4*4])))&0xffffffff
 m=ProbeMachine();load(m,0x40000000,count.to_bytes(4,'big')+(expected^(1 if corrupt else 0)).to_bytes(4,'big')+payload);m.endpoints=[0x80003cce,0x80003c4e];stoprun(m,0x80003bfa)
 check(f'checksum {count}/{corrupt}: actual decision',m.endpoint==(0x80003c4e if corrupt else 0x80003cce))
 cases.append({'kind':'actual complete bootstrap checksum loop and decision','bytes':count,'corrupt_stored_checksum':corrupt,'endpoint':hex(m.endpoint),'instructions':len(m.steps),'observation':'loop covers floor(length/4) words; odd tail is not included'})
# Outer main updater: injected failures at first erase, first program, and all operations.
for fail in ['none','erase','program','all']:
 m=ProbeMachine();m.map(0x4bc47084,4);m.map(0x401fa938,8);m.write(0x4bc47084,4,513);m.reg['a6']=0x30003000;m.endpoints=[0x4008aec2]
 m.stubs={0x400059c0:(1,0),0x400edbbe:(1,-1 if fail in ['erase','all'] else 0),0x400edb42:(3,-1 if fail in ['program','all'] else 0)}
 stoprun(m,0x4008ad76);erases=[x for x in m.calls if x[0]==0x400edbbe];writes=[x for x in m.calls if x[0]==0x400edb42]
 check(f'outer {fail}: reaches completion boundary',m.endpoint==0x4008aec2 and len(erases)==1 and len(writes)==2)
 cases.append({'kind':'actual outer main update loops with injected wrapper return values','injected_failure':fail,'erase_calls':len(erases),'program_calls':len(writes),'endpoint':hex(m.endpoint),'instructions':len(m.steps)})
# Real wrapper error propagation with supplied low-level operation failure.
for entry,args,geometry,fail,expected_calls in [(0x400edb42,(0x80000,512,0x29002000),256,1,1),(0x400edb42,(0x80000,512,0x29002000),256,2,2),(0x400edbbe,(0x80000,),0x10000,1,1)]:
 m=ProbeMachine();m.map(0x40200324,8);m.write(0x40200324,4,geometry);m.write(0x40200328,4,256);m.stubs={0x400ed520:(0,0)}
 low=0x400ecf7a if entry==0x400edb42 else 0x400ed272
 # Custom call result sequencing is implemented separately below.
 m.stubs[low]=(3 if entry==0x400edb42 else 1,-1);m.fail_call=fail;m.low=low;m.low_count=0
 original=dict(m.stubs)
 # Prefix machinery gains call-indexed failure without changing firmware.
 failure_source=new_source.replace("self.reg['d0']=result&0xffffffff;pc=self.get('(a7)+',4);continue", "if pc==getattr(self,'low',None):\n     self.low_count+=1;result=-1 if self.low_count==self.fail_call else 0\n    self.reg['d0']=result&0xffffffff;pc=self.get('(a7)+',4);continue")
 exec('if True:\n'+failure_source);Machine.run=run
 result=m.run(entry,args)
 check(f'wrapper {entry:x}/{fail}: propagates failure',result==0xffffffff and m.low_count==expected_calls)
 cases.append({'kind':'actual wrapper with injected low-level return','entry':hex(entry),'failed_call':fail,'return':hex(result),'low_calls':m.low_count,'instructions':len(m.steps)})
# Execute actual low-level command emission and status-poll cleanup. Hardware status is supplied.
for kind in ['program','erase']:
 for statuses,expected in [([0],0),([1,0],0),([0x61,0],0xffffffff),([0x60],0)]:
  m=ProbeMachine();m.status=list(statuses);load(m,0x29002000,bytes(range(17)))
  m.stubs={0x400ec63e:(0,0),0x400019e4:(1,0),0x400ea1e8:(1,0),0x400ec4cc:(0,0),0x400ec50e:(2,0),0x400ec5a8:(0,0),0x400ec5fc:(0,0),0x400ea27c:(0,0),0x40001b16:(1,0)}
  result=m.run(0x400ecf7a if kind=='program' else 0x400ed272,(0x80000,17,0x29002000) if kind=='program' else (0x80000,))
  resets=sum(pc==0x400ec5fc for pc,_ in m.calls)
  check(f'{kind} status {statuses}: actual returned status',result==expected)
  check(f'{kind} status {statuses}: actual cleanup',sum(pc==0x400ea27c for pc,_ in m.calls)==1 and sum(pc==0x40001b16 for pc,_ in m.calls)==1)
  check(f'{kind} status {statuses}: error cleanup only while busy',resets==(1 if statuses[0]==0x61 else 0))
  if kind=='program':check(f'program status {statuses}: actual command and payload',m.commands[0]&255==2 and [v&255 for v in m.commands[4:]]==list(range(17)))
  cases.append({'kind':'actual low-level '+kind+' command/poll/cleanup with simulated status boundary','status_values':statuses,'return':hex(result),'status_reset_calls':resets,'instructions':len(m.steps),'limitations':'mutex, bus-selection, write-enable, status-read/reset, and scheduling helper internals supplied at explicit boundaries'})
Machine.run=globals()['run']
# Actual wrapper + SPI emission for the final stock block: stale tail versus explicitly zeroed tail.
for prepare in [False,True]:
 m=ProbeMachine();m.map(0x40200324,8);m.write(0x40200324,4,0x10000);m.write(0x40200328,4,256)
 final_start=(length//512)*512;received_tail=bytes(decoded[8+final_start:]);image_tail=received_tail+bytes([165])*(512-len(received_tail));load(m,0x29002000,image_tail)
 if prepare:m.run(0x400ec284,(0x29002000+length-final_start,0,512-(length-final_start)))
 m.stubs={0x400ed520:(0,0),0x400ec63e:(0,0),0x400019e4:(1,0),0x400ea1e8:(1,0),0x400ec4cc:(0,0),0x400ec5a8:(0,0),0x400ec5fc:(0,0),0x400ea27c:(0,0),0x40001b16:(1,0)}
 result=m.run(0x400edb42,(0x80000+final_start,512,0x29002000));emitted=bytes(v&255 for v in m.commands[4:260]+m.commands[264:520])
 check(f'final stock block {prepare}: exact actual emitted 512 bytes',result==0 and len(m.commands)==520 and emitted==container[final_start:]+(bytes(304) if prepare else bytes(72)+bytes([165])*232))
 cases.append({'kind':'actual wrapper and low-level SPI emission of final stock block; simulated hardware','explicit_padding_prepared':prepare,'payload_tail_bytes':length-final_start,'wire_padding':72,'additional_tail_bytes':232,'additional_tail_value':0 if prepare else 165,'instructions':len(m.steps),'limitations':'initial tail is a controlled sentinel fixture, not a readout of device RAM; no physical flash written'})
# The bootstrap outer loops likewise do not branch on failed wrapper returns.
m=ProbeMachine();m.reg['d4']=513;m.endpoints=[0x80003fd8];m.stubs={0x80002f48:(1,-1),0x80002edc:(3,-1)};stoprun(m,0x80003f6a)
check('bootstrap outer loops ignore erase/program failures',len([x for x in m.calls if x[0]==0x80002f48])==1 and len([x for x in m.calls if x[0]==0x80002edc])==2)
cases.append({'kind':'actual bootstrap outer loops; all wrapper returns injected as -1','endpoint':hex(m.endpoint),'erase_calls':1,'program_calls':2,'instructions':len(m.steps)})
# Persistent busy has no observed firmware timeout: stop at a test-imposed poll count.
m=ProbeMachine();m.status_default=1;m.poll_limit=3;load(m,0x29002000,bytes(range(17)))
m.stubs={0x400ec63e:(0,0),0x400019e4:(1,0),0x400ea1e8:(1,0),0x400ec4cc:(0,0),0x400ec5a8:(0,0),0x400ec5fc:(0,0),0x400ea27c:(0,0),0x40001b16:(1,0)}
stoprun(m,0x400ecf7a,(0x80000,17,0x29002000))
check('persistent busy reaches third poll without cleanup',m.endpoint==0x400ec5a8 and not any(pc==0x400ea27c for pc,_ in m.calls))
cases.append({'kind':'actual program persistent-busy fixture','test_imposed_poll_limit':3,'firmware_return_observed':False,'instructions':len(m.steps),'limitation':'test stops the loop; does not establish a real-device permanent hang or hardware recovery behavior'})
# Safe final-block zero filling is demonstrated as a RAM-only preparation fixture.
for length_fixture in [1,511,512,513,length,length+4096]:
 payload=bytes((j*73+19)&255 for j in range(length_fixture));rounded=((length_fixture+511)//512)*512
 m=ProbeMachine();load(m,0x29002000,payload+bytes([0xa5])*(rounded-length_fixture))
 # Stock memset writes only the necessary zero tail; this is not an installed hook.
 if rounded>length_fixture:m.run(0x400ec284,(0x29002000+length_fixture,0,rounded-length_fixture))
 check(f'padding fixture {length_fixture}: payload unchanged',bytes(m.read(0x29002000+j,1) for j in range(length_fixture))==payload)
 check(f'padding fixture {length_fixture}: final block zeros',all(m.read(0x29002000+j,1)==0 for j in range(length_fixture,rounded)))
 cases.append({'kind':'RAM-only padding preparation using actual stock memset; not integrated or packaged','container_bytes':length_fixture,'write_bytes':rounded,'explicit_zero_tail_bytes':rounded-length_fixture,'instructions':len(m.steps)})
check('stock flash padding requires 304 bytes',((length+511)//512)*512-length==304)
check('stock wire leaves 232 final-block bytes unspecified',304-len(pad)==232)
check('original SysEx unchanged',hashlib.sha256(syx).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
pathlib.Path('outputs/Digitone-update-completion-results.json').write_text(json.dumps({'checks':checks,'check_count':len(checks),'cases':cases,'stock':{'container_bytes':length,'wire_decoded_bytes':len(decoded),'content_checksum':hex(stored),'wire_padding':len(pad),'flash_padding':304,'additional_unreceived_tail':232},'limits':['No firmware modifications or device I/O.','Notification and low-level flash operations use explicit test boundaries.','Full hardware receive session and unchanged memory tail provenance not established.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases)}))



