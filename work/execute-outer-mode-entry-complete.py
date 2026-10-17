"""Actual outer mode entry with explicit heap boundary and constructed page state."""
exec(open('work/execute-full-handler-transition.py').read().split('# Complete actual virtual entry')[0])
# The separate outer allocation creates a 16-byte page-list node; ownership
# pool allocators, retains, event copies and queue publication remain stock.
source=source.replace("assert size==1, ('unexpected heap allocation',size)","assert size in (1,16), ('unexpected heap allocation',size)")
source=source.replace("self.reg['d0']=0x27008000", "self.reg['d0']=0x27008000 if size==1 else 0x28001000")
exec('if True:\n'+source);Machine.run=run
RANGES.extend([(0x400d7a6e,0x400d7bcc),(0x400d6b90,0x400d6baa),(0x400d798a,0x400d7a6e),(0x400d6af2,0x400d6b3a),(0x400d6bb4,0x400d6bc0),(0x400d695c,0x400d6966),(0x400d7614,0x400d7620),(0x4012e9a8,0x4012e9bc),(0x40167298,0x401672be),(0x4015a5e2,0x4015a608),(0x40001a4c,0x40001ac4),(0x4012f8e8,0x4012f908),(0x40001b6e,0x40001bd6),(0x40130c4e,0x40130cea),(0x40016408,0x400165da),(0x400d75f4,0x400d75fe)])
M=0x28000000;TASK=0x28100000;CTX=0x28200000;REF=0x28300000
cases=[];checks=[]
def outer_state():
 m=state()
 for a,n in [(M,0x2000),(TASK,0x100),(CTX,0x100),(REF,8),(0x419a260c,4),(0x429a39a8,4)]:m.map(a,n)
 m.write(0x429a39a8,4,TASK)
 m.write(M+20,4,M+20);m.write(M+24,4,M+20);m.write(M+28,4,M+20)
 m.write(REF,4,PAGE);m.write(REF+4,4,0)
 m.write(PAGE+28,4,0);m.write(PAGE+32,4,0)
 m.write(0x419a260c,4,CTX);m.write(CTX+0xe8,4,2);m.write(CTX+0xe4,4,1)
 return m
for recursive in (False,True):
 m=outer_state()
 if recursive:m.write(M+8,4,TASK)
 p=pop(m,60);e=event(m,p);m.run(0x400f0690,(T,e));m.run(0x400f0886,(e,));qhead=m.read(0x4199fe94,4)
 cache=K+0x414+60*72;m.write(cache+56,4,p)
 begin=len(m.steps);ret=m.run(0x400d7a6e,(M,REF,0));path=m.steps[begin:]
 check(f'{recursive}: outer entry succeeds and returns',ret&255==1)
 check(f'{recursive}: actual list insertion and virtual callback executed',all(x in path for x in [0x40167298,0x400d798a,0x400d7bb0,0x400d6944,0x400d65d4,0x400d6d46,0x400ae458]))
 check(f'{recursive}: actual page receives manager',m.read(PAGE+44,4)==M)
 check(f'{recursive}: live ownership survives complete outer entry',m.read(p,4)==2 and m.read(T+56,4)==p and m.read(cache+56,4)==p and m.read(0x4199fe94,4)==qhead)
 check(f'{recursive}: both input gates survive',m.read(0x4131ba1c,4)==3 and m.read(0x4131ba40,4)==1)
 check(f'{recursive}: mask and outer mutex restored',m.sr&0xff00==0x2000 and m.read(M+8,4)==(TASK if recursive else 0) and m.read(M+4,4)==0)
 start=len(m.steps);m.run(0x400dc8c4,(MSG,3,8));handler=m.steps[start:]
 check(f'{recursive}: full accepted handler publishes after outer entry',0x400f0886 in handler and m.read(NOTIFY+4,4)==1)
 cases.append({'recursive':recursive,'outer_steps':[hex(x) for x in path],'handler_steps':[hex(x) for x in handler],'ownership_before_handler':{'ref':2,'template':hex(p),'cache':hex(p),'queue':hex(qhead)},'heap_boundary_calls':m.heap_calls,'page_manager':hex(m.read(PAGE+44,4))})
 print('OUTER',recursive,len(path),len(handler))
for condition in ['null page','already attached page']:
 m=outer_state()
 if condition=='null page':m.write(REF,4,0)
 else:m.write(PAGE+44,4,M)
 start=len(m.steps);ret=m.run(0x400d7a6e,(M,REF,0));path=m.steps[start:]
 check(condition+': outer precondition rejects entry',ret&255==0 and 0x400ae458 not in path)
 check(condition+': no heap allocation or producer shutdown',not m.heap_calls and m.read(0x4131ba40,4)==1)
 check(condition+': mutex restored on rejected exit',m.read(M+8,4)==0 and m.sr&0xff00==0x2000)
 cases.append({'condition':condition,'outer_steps':[hex(x) for x in path],'accepted':False})
pathlib.Path('outputs/Digitone-outer-mode-entry-complete-results.json').write_text(json.dumps({'checks':checks,'cases':cases,'firmware_modified':False,'limitations':['Page/manager/current-task/global context state supplied, not observed hardware state.','Heap returns supplied only for 16-byte UI node and one-byte closure; stock pool/event/ownership and kernel notification paths executed.','No contended mutex, ISR/task interleaving, child page or pending UI-context job execution.']},indent=2))


