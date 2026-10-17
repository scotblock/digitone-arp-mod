"""Execute actual cache builder/selectors/publisher, with controlled consumer boundaries."""
exec(open('work/execute-payload-lifecycle.py').read().split('checks=[];scenarios=[];total_steps=0')[0])
RANGES.extend([(0x400ef810,0x400efc4e),(0x400f04c0,0x400f0504),(0x400f06d4,0x400f06f2),(0x400f0886,0x400f08f0),(0x4009c2f8,0x4009c314)])
K=0x431d1758;S=0x24000000;D=0x25000000;N=0x26000000
def setup(mode=2,selector=0):
 m=fresh()
 for a,n in [(K,0x2a18*4),(S,0x146),(D,48),(N,64*20),(0x4199fe94,4)]:m.map(a,n)
 m.write(S+0x12a,4,mode);m.write(S+0x12e,4,selector);m.write(K+0x2a14,1,255)
 for j in range(64):m.write(N+j*20+16,4,N+(j+1)*20 if j<63 else 0)
 m.write(0x4199fe9c,4,N)
 return m
def emit(m,n,on,p=0):
 for j in range(48):m.write(D+j,1,0)
 for off,value in [(0,0),(4,n),(8,100),(12,1 if on else 2),(16,0x30001),(36,S),(40,p)]:m.write(D+off,4,value)
 m.run(0x400efa20,(D,))
def queued(m):
 nodes=[];events=[];node=m.read(0x4199fe94,4)
 while node:
  assert node not in nodes;nodes.append(node);assert m.read(node,4)==1
  e=m.read(node+8,4)
  while e:
   assert e not in [x['event'] for x in events]
   p=m.read(e+56,4)
   events.append({'event':e,'note':m.read(e+24,1),'onoff':m.read(e+4,4),'payload':p,'ref':m.read(p,4) if p else None,'tag':m.read(p+20,4) if p else None})
   e=m.read(e+68,4)
  node=m.read(node+16,4)
 return events
def consume(m):
 # This follows the confirmed event-retirement and node-retirement order.
 # Audio synthesis/arp acceptance itself remains outside this execution.
 before=queued(m);node=m.read(0x4199fe94,4)
 while node:
  e=m.read(node+8,4)
  while e:
   nxt=m.read(e+68,4);m.run(0x400f065c,(e,));e=nxt
  nxt=m.read(node+16,4);m.run(0x400f04f8,(nxt,));m.run(0x400f06d4,(node,));node=nxt
 return before
checks=[];cases=[]
def check(n,c):assert c,n;checks.append(n)
def snapshot(m,phase):
 return {'phase':phase,'selected':m.read(K+0x2a14,1),'queue':queued(m),'cache60':hex(m.read(K+0x414+60*72+56,4)),'cache64':hex(m.read(K+0x414+64*72+56,4)),'free_head':hex(m.read(0x4199fe98,4)),'ref_first':m.read(P,4),'tag_first':m.read(P+20,4)}
for mode in [2,3]:
 for selector,a,bnote in [(0,60,64),(1,64,60),(2,60,64)]:
  m=setup(mode,selector);trace=[]
  p=pop(m,a);emit(m,a,True,p);trace.append(snapshot(m,'A published'))
  check(f'{mode}/{selector}: A queued by actual publisher',len(queued(m))==1 and queued(m)[0]['payload']==p)
  consume(m);trace.append(snapshot(m,'A consumed'))
  bp=pop(m,bnote);emit(m,bnote,True,bp);trace.append(snapshot(m,'B published'))
  check(f'{mode}/{selector}: B reuses actual LIFO address',bp==p and m.read(K+0x414+a*72+56,4)==bp)
  consume(m);trace.append(snapshot(m,'B consumed'))
  emit(m,bnote,False);trace.append(snapshot(m,'B release publishes departing and A replay'))
  q=queued(m)
  check(f'{mode}/{selector}: builder publishes stale replay in departing-before-replay order',len(q)==2 and q[0]['onoff']==2 and q[0]['payload']==0 and q[1]['onoff']==1 and q[1]['note']==a and q[1]['payload']==p and q[1]['ref']==0 and q[1]['tag']==bnote)
  consume(m);trace.append(snapshot(m,'replay consumed'))
  check(f'{mode}/{selector}: retirement underflows replayed record',m.read(p,4)==0xffffffff)
  check(f'{mode}/{selector}: producer restores interrupt mask at each completed call',m.sr&0xff00==0x2000)
  cases.append({'name':f'completed producer/consumer ordering mode {mode} selector {selector}','trace':trace,'executed_steps':len(m.steps),'visited_addresses':[hex(a) for a in sorted(set(m.steps))]})

# Consumer postponed until after both input presses: no record is freed before
# replay, but three queued owners have only the two initial pop references.
m=setup();a=pop(m,60);emit(m,60,True,a);bp=pop(m,64);emit(m,64,True,bp);emit(m,64,False)
q=queued(m);check('deferred consumption still permits two queued copies of A with one ref',len(q)==4 and sum(e['payload']==a for e in q)==2 and m.read(a,4)==1)
before=snapshot(m,'all producers completed before consumer');consume(m)
check('deferred consumption underflows A after both queued owners retire',m.read(a,4)==0xffffffff)
cases.append({'name':'consumer deferred until all three inputs complete','trace':[before,snapshot(m,'consumer finished')],'executed_steps':len(m.steps)})

# Unselected note has a reference available for its first publication.
for selector,a,bnote in [(1,60,64),(2,64,60)]:
 m=setup(2,selector);ap=pop(m,a);emit(m,a,True,ap);bp=pop(m,bnote);emit(m,bnote,True,bp)
 check(f'unselected {selector}: actual builder returns without publication',len(queued(m))==1 and m.read(bp,4)==1)
 consume(m);emit(m,a,False);q=queued(m)
 check(f'unselected {selector}: later first publication has valid initial ref',len(q)==2 and q[1]['payload']==bp and q[1]['ref']==1)
 consume(m);check(f'unselected {selector}: balanced first retirement',m.read(bp,4)==0)
 cases.append({'name':f'unselected first transfer selector {selector}','trace':[snapshot(m,'first transfer completed')],'executed_steps':len(m.steps)})

# Event exhaustion is exercised through the actual builder, not a boolean.
m=setup();busy=[event(m) for _ in range(128)];p=pop(m,60);emit(m,60,True,p)
check('fresh allocation failure: builder updates cache but publishes nothing',not queued(m) and m.read(K+0x414+60*72+56,4)==p and m.read(p,4)==1)
emit(m,60,False)
check('failure followed by departure: actual cache overwrite drops positive reference',not queued(m) and m.read(K+0x414+60*72+56,4)==0 and m.read(p,4)==1)
cases.append({'name':'actual builder fresh allocation failure then departure','trace':[snapshot(m,'departure finished')],'executed_steps':len(m.steps)})

m=setup();a=pop(m,60);emit(m,60,True,a);consume(m);bp=pop(m,64);emit(m,64,True,bp);consume(m)
busy=[event(m) for _ in range(127)];emit(m,64,False);q=queued(m)
check('actual partial publication: departing event survives replacement allocation failure',len(q)==1 and q[0]['onoff']==2 and q[0]['payload']==0)
cases.append({'name':'actual builder second allocation failure','trace':[snapshot(m,'partial publication')],'executed_steps':len(m.steps)})

for mode in [0,1]:
 m=setup(mode);p=pop(m,60);emit(m,60,True,p);consume(m);bp=pop(m,64);emit(m,64,True,bp);consume(m);emit(m,64,False)
 check(f'mode {mode}: actual builder publishes no alternate cache replay',len(queued(m))==1 and queued(m)[0]['payload']==0)

# Execute the stock arp setup's disabled branch. This confirms that the
# supplied no-template scenario has an actual settings gate, rather than
# assuming every incoming note bypasses template retention.
RANGES.append((0x4009719e,0x4009743e))
m=setup();out=0x27000000;m.map(out,8);m.write(out,4,0x12345678)
m.write(S+0x10f,1,0)
result=m.run(0x4009719e,(0,1,C,0,0,2,S,out,out+4))
check('stock disabled-arp setup returns zero identity and clears mode output',result==0 and m.read(out,4)==0)
check('disabled-arp setup does not enter template-copy helper',0x400f0690 not in m.steps)
cases.append({'name':'actual disabled-arp acceptance gate','result':result,'mode_output':m.read(out,4),'executed_steps':len(m.steps),'visited_addresses':[hex(a) for a in sorted(set(m.steps))]})

# Payload-free controls execute the same selected-note routing. Null payloads
# avoid the reference failure even when input and retirement are batched.
for selector in range(3):
 m=setup(2,selector);emit(m,60,True);emit(m,64,True);emit(m,64,False);q=queued(m)
 check(f'payload-free selector {selector}: no queued payload ownership',all(e['payload']==0 for e in q))
 consume(m);check(f'payload-free selector {selector}: payload pool stays intact',len(freechain(m)['slots'])==64 and all(m.read(P+j*0x504,4)==0 for j in range(64)))

# Instruction anchors for the recovered task/consumer ordering. These do not
# replace execution of the complete ISR or its synthesis callbacks.
anchors={0x400db246:'4e90',0x400db2ac:'4e90',0x400db2fc:'6000fec8',0x4000173a:'203c407c2000',0x4009bd52:'23c0400002fc',0x4009cb66:'4eb9400f04f0',0x4009cb8e:'4a94',0x4009cb90:'6700038e',0x4009cef0:'242b0044',0x4009cef6:'4eb9400f065c',0x4009cf0a:'4eb9400f04f8',0x4009cf12:'4eb9400f06d4',0x400971b6:'4a29010f',0x400971ba:'660c',0x400971c2:'4280',0x4009de12:'4a83',0x4009de14:'670000f0'}
for a,h in anchors.items():assert b[a-base:a-base+len(bytes.fromhex(h))].hex()==h,(hex(a),h)
todo=[0x400db15a];task={}
while todo:
 a=todo.pop()
 if a in task:continue
 assert 0x400db15a<=a<0x400db300
 i=next(md.disasm(b[a-base:a-base+16],a,count=1));name=i.mnemonic.split('.')[0]
 assert i.id!=0 or bytes(i.bytes) in [bytes.fromhex(f'4a8{x:x}') for x in range(8,16)]
 task[a]={'bytes':i.bytes.hex(),'instruction':f'{i.mnemonic} {i.op_str}'}
 assert name not in ('rts','rte','jmp','trap')
 if name.startswith('b') and name not in ('bsr','btst'):
  todo.append(int(re.findall(r'\$([0-9a-f]+)',i.op_str)[0],16))
  if name!='bra':todo.append(a+i.size)
 else:todo.append(a+i.size)
assert not any(re.search(r'\bsr\b',v['instruction']) for v in task.values())

source=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(source.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
assert hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6']
pathlib.Path('outputs/Digitone-producer-consumer-ordering-results.json').write_text(json.dumps({'firmware_modified':False,'sha256':hashes,'checks':checks,'cases':cases,'verified_anchors':{hex(a):h for a,h in anchors.items()},'midi_task_local_graph':{hex(a):v for a,v in sorted(task.items())},'executed_ranges':[[hex(a) for a in r] for r in RANGES],'scope':'Actual cache builder, selectors, publisher, allocation/copy/release helpers and disabled-arp setup branch. Consumer retirement follows recovered firmware order; synthesis, full ISR, enabled-arp acceptance and upstream note descriptor construction are not executed.','limitation':'Shows ordering permitted by these actual local routines under supplied valid inputs. Does not independently validate custom interpreter or prove a hardware defect.'},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'cases':len(cases),'instructions_in_recorded_cases':sum(c['executed_steps'] for c in cases),'hashes_unchanged':True},indent=2))
