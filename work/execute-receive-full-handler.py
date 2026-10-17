"""Receive task continuation through complete stock handler; explicit failure case."""
exec(open('work/execute-full-handler-transition.py').read().split('# Complete actual virtual entry')[0])
source=source.replace('def run(self,entry,args=()):','def until(self,entry,stop):')
source=source.replace("  for v in reversed(args):self.put('-(a7)',4,v)\n  self.put('-(a7)',4,0xffffffff);pc=entry",'  pc=entry')
source=source.replace('if pc==0xffffffff:break','if pc==stop:break')
source=source.replace("  self.reg['a7']+=len(args)*4",'').replace("  assert self.reg['a7']==initial_sp",'').replace("  assert all(self.reg[r]==v for r,v in saved.items())",'')
exec('if True:\n'+source);Machine.until=until
RANGES.append((0x400db202,0x400db24c))
cases=[];checks=[]
for receive_gate,note_gate,exhausted in [(0,1,False),(1,0,False),(1,1,False),(1,1,True)]:
 m=state(note_gate,True,0);m.run(0x400d6944,(PAGE,0x28000000))
 if exhausted:
  busy=[event(m) for j in range(128)]
  check('failure case exhausts actual 128-event allocator',len(set(busy))==128 and m.read(0x4199fea0,4)==0)
 m.write(0x4131ba1c,4,receive_gate)
 Q=MSG+16;m.write(Q,4,3);m.write(Q+4,4,MSG)
 m.reg['d0']=Q;m.reg['a2']=0x401aade0;m.reg['a7']=0x30002000
 start=len(m.steps);m.until(0x400db202,0x400db24c);path=m.steps[start:]
 accepted=bool(receive_gate and note_gate)
 check(f'{receive_gate}/{note_gate}/{exhausted}: actual dispatch obeys first gate',(0x400dc8c4 in path)==bool(receive_gate))
 check(f'{receive_gate}/{note_gate}/{exhausted}: actual producer obeys second gate',(0x400dc432 in path)==accepted)
 check(f'{receive_gate}/{note_gate}/{exhausted}: completed handler returned to receive loop',m.reg['a7']==0x30002004)
 check(f'{receive_gate}/{note_gate}/{exhausted}: scheduler publication result',bool(m.read(0x4199fe94,4))==bool(accepted and not exhausted))
 check(f'{receive_gate}/{note_gate}/{exhausted}: input notification survives event allocation failure',m.read(NOTIFY+4,4)==int(accepted))
 check(f'{receive_gate}/{note_gate}/{exhausted}: payload acquired only on accepted path',m.read(P,4)==int(accepted))
 if accepted:
  check(f'{exhausted}: actual cache holds payload',m.read(K+0x414+60*72+56,4)==P)
  check(f'{exhausted}: actual registry records note/flags',m.read(REG+4,1)==60 and m.read(REG,4)==8)
 cases.append({'receive_gate':receive_gate,'note_gate':note_gate,'events_exhausted':exhausted,'steps':[hex(x) for x in path],'queue_head':hex(m.read(0x4199fe94,4)),'payload_ref':m.read(P,4),'notifications':m.read(NOTIFY+4,4),'sr':hex(m.sr)})
 print('RECEIVE',receive_gate,note_gate,exhausted,len(path))
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
check('source images unchanged',hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'])
pathlib.Path('outputs/Digitone-receive-full-handler-results.json').write_text(json.dumps({'checks':checks,'cases':cases,'sha256':hashes,'firmware_modified':False,'limitations':['Actual first-queue receive continuation starts with a supplied packet; kernel receive wait not executed.','Assigned synth track zero, channel zero, velocity 100, note 60, single-note setting, flags 8, selected step zero.','Real RAM values, input gate writers, concurrent producers and peripheral behavior not observed.','Heap boundary only for one-byte UI callable copy; no ownership or publication helpers stubbed.']},indent=2))
