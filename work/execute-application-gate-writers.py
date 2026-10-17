"""Read-only config gate writers and application selected-page helper execution."""
exec(open('work/execute-outer-mode-entry-complete.py').read().split('for recursive in (False,True):')[0])
RANGES.extend([(0x40013722,0x400138de),(0x400135a0,0x40013722),(0x4002af1a,0x4002af70),(0x4002b344,0x4002b38e),(0x4002b38e,0x4002b3e2),(0x40138354,0x4013835e),(0x401386a8,0x40138720),(0x40131922,0x40131978),(0x400a8d90,0x400a8de4),(0x400d5f02,0x400d5f64),(0x4015a304,0x4015a340),(0x4013e262,0x4013e280),(0x4012c344,0x4012c392)])
CF=0x4131b990;OBJ=0x28401000;APP=0x28600000;CONTROL=0x28700000
checks=[];cases=[]
def writer_state():
 m=outer_state();m.map(CF,0x2ebc);m.map(OBJ,0x100)
 m.write(OBJ,4,0x40174fc8);m.write(OBJ+16,4,CF)
 return m
for full in (0,1):
 m=writer_state();start=len(m.steps);m.run(0x40013722,(CF,full));path=m.steps[start:]
 check(f'default init {full}: enables both receive sources',m.read(0x4131ba1c,4)==3)
 check(f'default init {full}: enables note reception',m.read(0x4131ba40,4)==1)
 check(f'default init {full}: publishes ordinary 0..7 channels',all(m.read(CF+0x58+j*4,4)==j for j in range(8)))
 cases.append({'name':'complete config defaults','full':full,'steps':[hex(x) for x in path],'gates':[m.read(CF+0x8c,4),m.read(CF+0xb0,4)]})
for value,want in [(-1,0),(0,0),(1,1),(2,2),(3,3),(4,3)]:
 m=writer_state();m.write(CF+0xb0,4,1);start=len(m.steps);m.run(0x4002af1a,(OBJ,value));path=m.steps[start:]
 check(f'receive setter {value}: clamps to 0..3',m.read(CF+0x8c,4)==want)
 check(f'receive setter {value}: actual getter and notification execute',0x40138354 in path and 0x401386a8 in path and 0x400a8d90 in path)
 check(f'receive setter {value}: other gate unchanged',m.read(CF+0xb0,4)==1)
 cases.append({'name':'complete receive mask setter','input':value,'expected':want,'steps':[hex(x) for x in path]})
for value in [0,1,2,255,256]:
 m=writer_state();m.write(CF+0x8c,4,3);start=len(m.steps);m.run(0x4002b344,(OBJ,value));path=m.steps[start:]
 check(f'note setter {value}: uses low byte',m.read(CF+0xb0,4)==value%256)
 check(f'note setter {value}: receive mask unchanged',m.read(CF+0x8c,4)==3)
 cases.append({'name':'complete note flag setter','input':value,'steps':[hex(x) for x in path]})
for initial,want in [(0,1),(1,0),(255,0)]:
 m=writer_state();m.write(CF+0xb0,4,initial);start=len(m.steps);m.run(0x4002b38e,(OBJ,));path=m.steps[start:]
 check(f'note toggle {initial}: actual boolean toggle',m.read(CF+0xb0,4)==want)
 cases.append({'name':'complete note toggle','initial':initial,'steps':[hex(x) for x in path]})
# Disabled gates do not retire preexisting owners, even when actual setters and
# their stock empty-observer notification returns are used.
m=writer_state();m.write(CF+0xb0,4,1);m.write(CF+0x8c,4,3)
p=pop(m,60);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f0886,(e,));qh=m.read(0x4199fe94,4)
start=len(m.steps);m.run(0x4002af1a,(OBJ,0));m.run(0x4002b344,(OBJ,0));path=m.steps[start:]
check('actual gate setters disable both gates',m.read(CF+0x8c,4)==0 and m.read(CF+0xb0,4)==0)
check('disabling gates leaves preexisting counted and queued owners',m.read(p,4)==2 and m.read(T+56,4)==p and m.read(0x4199fe94,4)==qh)
cases.append({'name':'disable gates with retained and queued owners','steps':[hex(x) for x in path],'refs':m.read(p,4),'queue_head':hex(qh)})
# Actual higher selected-child helper: assigns owning child reference, invokes
# outer entry, then releases temporary UI references.
m=outer_state();m.map(APP,0x300);m.map(CONTROL,16)
m.write(APP+0x64,4,M);m.write(APP+0x2b4,4,PAGE);m.write(APP+0x2b8,4,CONTROL);m.write(CONTROL+4,4,1)
p=pop(m,60);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f0886,(e,));qh=m.read(0x4199fe94,4)
start=len(m.steps);ret=m.run(0x400d5f02,(APP,APP+0x2b4));path=m.steps[start:]
check('selected-child helper completes actual mode entry',ret&255==1 and 0x400d7a6e in path and 0x400ae458 in path)
check('selected-child helper publishes parent selected page',m.read(APP+0x84,4)==PAGE and m.read(APP+0x88,4)==CONTROL)
check('UI page reference accounting balanced',m.read(CONTROL+4,4)==3)
check('application helper leaves gates enabled',m.read(0x4131ba1c,4)==3 and m.read(0x4131ba40,4)==1)
check('application helper preserves live note ownership',m.read(p,4)==2 and m.read(T+56,4)==p and m.read(0x4199fe94,4)==qh)
cases.append({'name':'complete application selected-child helper to audio mode','steps':[hex(x) for x in path],'ui_ref_count':m.read(CONTROL+4,4),'payload_refs':m.read(p,4),'gates':[m.read(0x4131ba1c,4),m.read(0x4131ba40,4)],'heap_boundary_calls':m.heap_calls})
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
hashes=[hashlib.sha256(syx.read_bytes()).hexdigest(),hashlib.sha256(b).hexdigest()]
check('source images unchanged',hashes==['0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda','ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6'])
pathlib.Path('outputs/Digitone-application-gate-writer-execution-results.json').write_text(json.dumps({'checks':checks,'cases':cases,'sha256':hashes,'firmware_modified':False,'limitations':['Synthetic initialized application, page, project and task state; not a captured device state.','Actual normal-menu registration does not select audio-test page; helper is called with its constructed field explicitly for this test.','Gate setters use the recovered config vtable with empty observer lists. Nonempty observer side effects remain open.','One-byte callable and 16-byte UI-node heap boundaries supplied; ownership helpers remain actual stock instructions.','No concurrent task/ISR/DMA or full startup execution.']},indent=2))
print(json.dumps({'checks':len(checks),'cases':len(cases),'recorded_steps':sum(len(c['steps']) for c in cases)}))


