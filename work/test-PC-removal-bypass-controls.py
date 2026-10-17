from pathlib import Path
exec(Path('work/test-PC-rejection-continuations.py').read_text().split('for recursive in [False,True]:')[0].split('for command,boundary')[0])
# Import fixture without running its command/manager tests.
source=Path('work/test-PC-rejection-continuations.py').read_text();a=source.index('def pagefixture(');z=source.index('\nfor recursive in [False,True]:',a);exec(source[a:z])
results=[]
import hashlib
stock_state_of=state_of
def state_of(m):
 out=stock_state_of(m);u=m.uc
 out['pool_hash']=hashlib.sha256(bytes(u.mem_read(0x419eb92c,0x3000))).hexdigest()
 out['context_hash']=hashlib.sha256(bytes(u.mem_read(0x47be1000,0xb74))+bytes(u.mem_read(LIVE['state'],LIVE['state_bytes']))).hexdigest()
 return out
def setup(recursive,name):
 m,M,N,P=pagefixture(recursive);u=m.uc;C=M+0x5000;H=M+0x6000;m.ensure(M-0x40);u.mem_write(0x419f0e50,u32(M-0x40));u.mem_write(P+0x28,u32(name));u.mem_write(C,u32(0x40192020)+u32(2)+u32(2)+u32(P));u.mem_write(N+0xc,u32(C));u.mem_write(H,u32(P)+u32(C));u.mem_write(0x4137c72c,u32(1));return m,M,N,P,C,H
for recursive in [False,True]:
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;before=state_of(m);page=bytes(u.mem_read(P,0x50));node=bytes(u.mem_read(N,16));refs=bytes(u.mem_read(C,16));regs=saved(u)
 execute_until(m,0x400e64b0,[M,H],0x400e64c0,sr=0x201f);u.emu_start(0x400e64c8,0xdeadbee0,count=100000)
 balanced(u,regs);assert u.reg_read(UC_M68K_REG_D0)&255==0 and before==state_of(m) and page==bytes(u.mem_read(P,0x50)) and node==bytes(u.mem_read(N,16)) and refs==bytes(u.mem_read(C,16))
 results.append({'kind':'direct removal false return before lock/reference acquisition','recursive':recursive,'state_and_references_preserved':True,'native_false_epilogue_balanced':True,'host_guard_selected':True});print('PASS direct guard',recursive,flush=True)
# Deny under the real mutex after the weak handle has been resolved into
# a strong temporary; skip selection recomputation but release temp and lock.
for recursive in [False,True]:
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;before=state_of(m);page=bytes(u.mem_read(P,0x50));node=bytes(u.mem_read(N,16));refs=bytes(u.mem_read(C,16));regs=saved(u)
 execute_until(m,0x400e64b0,[M,H],0x400e6500,sr=0x201f);assert rd(u,C+4)==3 and rd(u,M+8)==M+0x8000
 u.reg_write(UC_M68K_REG_D3,0);u.emu_start(0x400e654c,0xdeadbee0,count=100000)
 balanced(u,regs);assert u.reg_read(UC_M68K_REG_D0)&255==0 and before==state_of(m) and page==bytes(u.mem_read(P,0x50)) and node==bytes(u.mem_read(N,16)) and refs==bytes(u.mem_read(C,16)) and rd(u,M+8)==(M+0x8000 if recursive else 0) and rd(u,M+4)==0
 results.append({'kind':'locked direct-removal rejection','recursive':recursive,'native_strong_temporary_acquired_and_released':True,'native_mutex_acquired_and_released':True,'selection_recompute_skipped':True,'page_pool_and_context_preserved':True,'host_guard_and_false_result_supplied':True});print('PASS locked direct guard',recursive,flush=True)
for name,label in [(0x401e197a,'AudioTestMenuView'),(0x401dfe30,'UI Test View')]:
 for recursive in [False,True]:
  m,M,N,P,C,H=setup(recursive,name);u=m.uc;before=state_of(m);refs=bytes(u.mem_read(C,16));pages=bytes(u.mem_read(P,0x50));node=bytes(u.mem_read(N,16));calls=[];regs=saved(u)
  def deny(u,pc,n,d):calls.append(pc);u.reg_write(UC_M68K_REG_D3,0);u.reg_write(UC_M68K_REG_PC,0x400e654c)
  h=u.hook_add(UC_HOOK_CODE,deny,begin=0x400e6500,end=0x400e6500)
  # Real singleton getter, name lookup, ref operations, directed caller and cleanup.
  execute_until(m,0x4008de1e,[],0x4008deae,sr=0x201f);u.emu_start(0x4008deae,0xdeadbee0,count=10);u.hook_del(h)
  balanced(u,regs);assert before==state_of(m) and refs==bytes(u.mem_read(C,16)) and pages==bytes(u.mem_read(P,0x50)) and node==bytes(u.mem_read(N,16)) and rd(u,0x4137c72c)==0 and len(calls)==int(label=='UI Test View') and rd(u,M+8)==(M+0x8000 if recursive else 0) and rd(u,M+4)==0
  results.append({'kind':'actual UI-abort caller','page_name':label,'recursive':recursive,'direct_remover_reached':bool(calls),'native_lookup_and_reference_cleanup':True,'refs_and_linked_page_preserved':True,'caller_clears_UI_test_flag_even_if_removal_refused':True,'host_guard_supplied_when_matched':True});print('PASS caller',label,recursive,flush=True)
# Execute the unreferenced front-node remover with a real heap-backed node.
for recursive in [False,True]:
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;allocated=call(m,0x400e96c0,[16],stack_top=RESETSTACK,limit=100000);u.mem_write(allocated,u32(M+20)+u32(M+20)+u32(P)+u32(C));u.mem_write(M+20,u32(allocated)+u32(allocated));before=state_of(m);exits=[];frees=[]
 h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:exits.append(pc),begin=0x400b25c2,end=0x400b25c2)
 h2=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:frees.append(rd(u,u.reg_read(UC_M68K_REG_A7)+4)),begin=0x400e96cc,end=0x400e96cc)
 regs=saved(u);execute_until(m,0x400e65dc,[M],0x400e6632,sr=0x201f);u.emu_start(0x400e6632,0xdeadbee0,count=10);u.hook_del(h);u.hook_del(h2)
 balanced(u,regs);assert before==state_of(m) and rd(u,M+20)==M+20 and rd(u,M+24)==M+20 and not exits and allocated in frees and rd(u,C+4)==1 and rd(u,M+8)==(M+0x8000 if recursive else 0) and rd(u,M+4)==0
 results.append({'kind':'front-node remover execution','recursive':recursive,'native_unlink_reference_drop_heap_free_and_unlock':True,'exit_callback_not_called':True,'note_state_preserved':True,'constructed_direct_invocation_no_reachable_caller_established':True});print('PASS front remover',recursive,flush=True)
Path('outputs/Digitone-E04-PC-removal-bypass-controls.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'cases':results,'limits':['Application/page/list/reference/task fixtures constructed; no physical device or contended scheduling.','Direct rejection is supplied by a host code hook; native epilogues/caller cleanup execute.','Front remover has no recovered direct/literal reference in MAIN; computed callers not exhausted.','Only the recovered UI-abort name selection is executed; all selection/closing routes are not certified.']},indent=2))
