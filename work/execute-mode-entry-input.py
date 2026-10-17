"""Read-only mode-entry ownership and MIDI-dispatch checks."""
exec(open('work/execute-shutdown-callback.py').read().split('# Existing page-entry helper')[0])
RANGES.extend([(0x400ae458,0x400ae45e),(0x400f04c0,0x400f0504),(0x400f06d4,0x400f06f2),(0x400f0886,0x400f08f0),(0x400db202,0x400db24c)])
checks=[];cases=[]
T=0x41345f08
K=0x431d1758
def mode_state():
 m=setup_state()
 for a,n in [(0x4199fe94,4),(0x26000000,20),(0x4131b9e4,4),(0x4131ba1c,4),(0x401aade0,64),(0x29000000,32),(K,4*0x2a18)]:m.map(a,n)
 m.write(0x4199fe9c,4,0x26000000)
 for k in range(0,64,4):m.write(0x401aade0+k,4,struct.unpack_from('>I',b,0x401aade0-base+k)[0])
 m.write(0x4131ba1c,4,3)
 return m
m=mode_state();p=pop(m,60);e=event(m,p);m.run(0x400f0690,(T,e));m.write(K+0x414+60*72+56,4,p)
m.run(0x400f0886,(e,));head=m.read(0x4199fe94,4)
check('queue event plus retained template have two references',m.read(p,4)==2 and head!=0)
start=len(m.steps);m.run(0x400ae458)
check('registered entry invoker installs alternate audio handler',m.read(0x400002fc,4)==0x400d924e)
check('mode entry leaves queue and counted owners intact',m.read(0x4199fe94,4)==head and m.read(p,4)==2 and m.read(T+56,4)==p)
check('mode entry leaves cached pointer intact',m.read(K+0x414+60*72+56,4)==p)
check('mode entry leaves both MIDI input bits enabled',m.read(0x4131ba1c,4)==3)
check('mode entry preserves caller interrupt mask',m.sr&0xff00==0x2000)
cases.append({'name':'registered mode-entry callback with existing owners','steps':[hex(x) for x in m.steps[start:]],'references':m.read(p,4),'queue_head':hex(head),'midi_bits':m.read(0x4131ba1c,4)})
# After the same actual mode-entry callback, execute the first receive queue's
# packet-dispatch branch. Stop at NoteOn handler entry; not full note production.
for enabled in [False,True]:
 m=mode_state();m.write(0x4131ba1c,4,1 if enabled else 0);m.run(0x400ae458)
 check('mode entry preserves supplied enabled or disabled receive gate',m.read(0x4131ba1c,4)==(1 if enabled else 0))
 Q=0x29000000;MSG=Q+16;m.write(Q,4,3);m.write(Q+4,4,MSG)
 for j,v in enumerate([0x90,60,100]):m.write(MSG+j,1,v)
 m.reg['d0']=Q;m.reg['a2']=0x401aade0;m.reg['a7']=0x30002000
 start=len(m.steps);m.until(0x400db202,0x400dc8c4 if enabled else 0x400db24c)
 path=m.steps[start:]
 check('enabled gate dispatches and disabled gate bypasses NoteOn', (0x400db246 in path)==enabled)
 check('mode vector unaffected by packet branch',m.read(0x400002fc,4)==0x400d924e)
 cases.append({'name':'first receive queue NoteOn gate','enabled':enabled,'steps':[hex(x) for x in path],'endpoint':hex(0x400dc8c4 if enabled else 0x400db24c)})
m=mode_state();m.write(0x4131ba1c,4,0);m.run(0x400ae458)
Q=0x29000000;MSG=Q+16;m.write(Q,4,3);m.write(Q+4,4,MSG);m.write(MSG,1,0xf0)
m.reg['d0']=Q;m.reg['a2']=0x401aade0;m.reg['a7']=0x30002000
target=m.read(0x401aade0+15*4,4);start=len(m.steps);m.until(0x400db202,target)
path=m.steps[start:]
check('disabled receive bits still dispatch SysEx',0x400db246 in path and 0x400db222 not in path)
cases.append({'name':'first receive queue SysEx with ordinary input disabled','steps':[hex(x) for x in path],'endpoint':hex(target),'receive_bits':m.read(0x4131ba1c,4)})
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
check('hashes unchanged',hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'])
pathlib.Path('outputs/Digitone-mode-entry-ownership-input-results.json').write_text(json.dumps({'firmware_modified':False,'checks':checks,'cases':cases,'sha256':hashes,'limitations':['Entry is registered callback invoker, not full outer mode-entry task.','Controlled preexisting owners and input-enable bits; real UI reachability not proven.','MIDI execution begins at already-dequeued first-queue packet branch and stops at NoteOn handler entry.','No task scheduling, ISR, full upstream producer or hardware execution.','Second receive queue gate inspected structurally only.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'steps':sum(len(c['steps']) for c in cases),'hashes_unchanged':True}))
