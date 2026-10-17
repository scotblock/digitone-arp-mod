"""Real 1.44 page remover, mutex and callback manager through reset entry.
Constructed page/list/task fixture; actual stock heap allocates the closure."""
from pathlib import Path
exec(Path('work/test-PC-diagnostic-command-exit.py').read_text().split('\nresults=[]')[0])
results=[]
for recursive in [False,True]:
 m=prepared();u=m.uc;queue_note(m,64);queue_note(m,67);u.mem_write(0x41368d64,u32(3));u.mem_write(0x41368d88,u32(1));u.mem_write(LIVE['state']+64*4,u32(0x800000be));u.mem_write(LIVE['pending'],u32(0x47fc8000)+u32(0x800000be));u.mem_write(0x402296f0,u32(rd(u,0x402296f0)&~0x80000))
 call(m,0x400b25bc,[],stack_top=RESETSTACK,limit=100000)
 M=0x47fb0000;NODE=M+0x1000;PAGE=M+0x2000;V=M+0x3000;TASK=M+0x8000;m.ensure(M);u.mem_write(M,bytes(0x9000));u.mem_write(0x429f2188,u32(TASK))
 if recursive:u.mem_write(M+8,u32(TASK))
 u.mem_write(M+20,u32(NODE)+u32(NODE));u.mem_write(NODE,u32(M+20)+u32(M+20)+u32(PAGE));u.mem_write(PAGE,u32(0x401c4714));u.mem_write(PAGE+0x30,b'\1');u.mem_write(PAGE+0x2c,u32(M));u.mem_write(PAGE+0x40,u32(V)+u32(V+16)+u32(V+16));u.mem_write(V,u32(V+0x100)+u32(0)+u32(0x400b2666)+u32(0x400b25c2))
 before=state_of(m);hits=[];heap=[]
 for pc in [0x400e6698,0x400e569a,0x400b25c2,0x4009d0ea,0x4009c5a4,0x40001aa4,0x400e96c0]:
  def hit(u,pc,n,d):
   hits.append({'pc':hex(pc),'SR':hex(u.reg_read(UC_M68K_REG_SR))})
   if pc==0x400e96c0:heap.append(rd(u,u.reg_read(UC_M68K_REG_A7)+4))
  u.hook_add(UC_HOOK_CODE,hit,begin=pc,end=pc)
 state=execute_until(m,0x400e6634,[M],ENTRY,sr=0x201f);after=state_of(m)
 assert before==after and (state[UC_M68K_REG_SR]>>8)&7==0 and rd(u,M+8)==TASK and rd(u,M+4)==int(recursive) and rd(u,M+20)==NODE
 assert heap==[1] and all(any(x['pc']==hex(pc) for x in hits) for pc in [0x400e6698,0x400e569a,0x400b25c2,0x4009d0ea,0x4009c5a4,0x40001aa4])
 results.append({'recursive_mutex':recursive,'before':before,'before_reset':after,'actual_path':hits,'actual_heap_requests':heap,'mutex_owner_at_reset':hex(rd(u,M+8)),'recursion_at_reset':rd(u,M+4),'page_still_linked':rd(u,M+20)==NODE,'passed':True})
 print('PASS native page exit',recursive,flush=True)
Path('outputs/Digitone-E04-PC-diagnostic-page-exit.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':results,'limits':['Page/list/callable/task/queued-event conditions constructed; actual prior application menu selection not executed.','Actual stock closure heap allocation executes; no allocator return stub.','No contended mutex/scheduler trap or interrupt/task interleaving; stop precedes pool reconstruction and normal callback cleanup.','Audio-test page entry differs from ENTER_TEST_MODE command entry.']},indent=2))
