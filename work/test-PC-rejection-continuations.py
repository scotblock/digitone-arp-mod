from pathlib import Path
exec(Path('work/test-PC-reinitialization-admission.py').read_text().split('\nm=prepared();u=m.uc;state=stage')[0])
from unicorn import UC_HOOK_MEM_WRITE
results=[]
CALLEE=[UC_M68K_REG_D0+i for i in range(2,8)]+[UC_M68K_REG_A0+i for i in range(2,7)]
def saved(u):return [u.reg_read(r) for r in CALLEE]
def balanced(u,regs):assert u.reg_read(UC_M68K_REG_A7)==0x47fdff04 and saved(u)==regs and u.reg_read(UC_M68K_REG_SR)&0xff00==0x2000
for command,boundary in [('ENTER',0x4008b85a),('EXIT',0x4008b88a)]:
 m=prepared();u=m.uc
 # Execute the same stock parser/selector with the requested token.
 source=Path('work/test-PC-reinitialization-admission.py').read_text(); fn=source[source.index('def stage('):source.index('\nm=prepared();u=m.uc;state=stage')].replace('#EXIT_TEST_MODE','#'+command+'_TEST_MODE')
 ns={};exec(fn,globals(),ns);s=ns['stage'](m,boundary);before=state_of(m);sp=u.reg_read(UC_M68K_REG_A7);a6=u.reg_read(UC_M68K_REG_A6);hits=[]
 textaddr=0x47fc7800;u.mem_write(textaddr,b'UNSUPPORTED: restart required\r\n\0')
 def print_arg(u,pc,n,d):
  assert rd(u,u.reg_read(UC_M68K_REG_A7))==0x401df570
  u.mem_write(u.reg_read(UC_M68K_REG_A7),u32(textaddr));hits.append('replacement rejection message supplied')
 h=u.hook_add(UC_HOOK_CODE,print_arg,begin=0x4008b870,end=0x4008b870)
 # Host chooses a proposed rejection continuation; the stock PEA/printf/
 # cleanup/loop branch itself executes. No persistent binary overlay.
 u.emu_start(0x4008b86a,0x4008b4ae,count=100000);u.hook_del(h)
 assert u.reg_read(UC_M68K_REG_PC)==0x4008b4ae and u.reg_read(UC_M68K_REG_A7)==sp and u.reg_read(UC_M68K_REG_A6)==a6 and before==state_of(m) and len(hits)==1
 results.append({'kind':'command rejection continuation','command':command,'pre_mutation':hex(boundary),'native_printf_cleanup_loop':True,'stack_and_frame_balanced':True,'state_preserved':True,'selection_and_message_pointer_supplied_by_host':True})
 print('PASS command',command,flush=True)

# Constructed page manager with actual stock mutex/task and page vtable.
def pagefixture(recursive):
 m=prepared();u=m.uc;queue_note(m,64);queue_note(m,67);u.mem_write(0x41368d64,u32(3));u.mem_write(0x41368d88,u32(1))
 M=0x47fb0000;N=M+0x1000;P=M+0x2000;V=M+0x3000;T=M+0x8000;m.ensure(M);u.mem_write(M,bytes(0x9000));u.mem_write(0x429f2188,u32(T))
 if recursive:u.mem_write(M+8,u32(T))
 u.mem_write(M+20,u32(N)+u32(N));u.mem_write(N,u32(M+20)+u32(M+20)+u32(P));u.mem_write(P,u32(0x401c4714));u.mem_write(P+0x2c,u32(M));u.mem_write(P+0x40,u32(V)+u32(V+16)+u32(V+16));u.mem_write(V,u32(V+0x100)+u32(0)+u32(0x400b2666)+u32(0x400b25c2))
 return m,M,N,P

for recursive in [False,True]:
 # Selection: acquire the real lock, deny before scanning/replacing children,
 # follow the existing false-return/unlock epilogue.
 m,M,N,P=pagefixture(recursive);u=m.uc;S=0x47fb4000;u.mem_write(S,u32(P));before=state_of(m);pages=bytes(u.mem_read(M+20,16))+bytes(u.mem_read(P,0x50));args=[M,S,0]
 regs=saved(u);s=execute_until(m,0x400e6352,args,0x400e637c,sr=0x201f);u.reg_write(UC_M68K_REG_D2,0);u.emu_start(0x400e649a,0xdeadbee0,count=100000)
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and u.reg_read(UC_M68K_REG_D0)&255==0 and before==state_of(m) and pages==bytes(u.mem_read(M+20,16))+bytes(u.mem_read(P,0x50)) and rd(u,M+8)==(0x47fb8000 if recursive else 0) and rd(u,M+4)==0
 balanced(u,regs)
 results.append({'kind':'selection rejection','recursive':recursive,'native_unlock_and_false_return':True,'page_and_note_state_preserved':True,'host_denial_before_manager_mutations':True})
 print('PASS selection',recursive,flush=True)
 # Close request: existing refusal branch before close flag/manager request.
 m,M,N,P=pagefixture(recursive);u=m.uc;before=state_of(m);pages=bytes(u.mem_read(M,0x40))+bytes(u.mem_read(P,0x50));regs=saved(u);s=execute_until(m,0x400e5442,[P],0x400e5454,sr=0x201f);u.reg_write(UC_M68K_REG_D0,1);u.emu_start(0x400e5454,0xdeadbee0,count=10000)
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and before==state_of(m) and pages==bytes(u.mem_read(M,0x40))+bytes(u.mem_read(P,0x50))
 balanced(u,regs)
 results.append({'kind':'close request rejection','recursive':recursive,'existing_refusal_branch_executed':True,'close_and_manager_flags_unchanged':True,'host_predicate_result_supplied':True})
 print('PASS close request',recursive,flush=True)
 # Already pending close: skip only this page inside remover, use normal unlock.
 m,M,N,P=pagefixture(recursive);u=m.uc;u.mem_write(P+0x30,b'\1');u.mem_write(M+0x22,b'\1');before=state_of(m);node=bytes(u.mem_read(N,12));page=bytes(u.mem_read(P,0x50));callbacks=[]
 h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:callbacks.append(hex(pc)),begin=0x400e6698,end=0x400e6698)
 regs=saved(u);s=execute_until(m,0x400e6634,[M],0x400e668a,sr=0x201f);u.reg_write(UC_M68K_REG_D0,0);u.emu_start(0x400e668a,0xdeadbee0,count=100000);u.hook_del(h)
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and before==state_of(m) and node==bytes(u.mem_read(N,12)) and page==bytes(u.mem_read(P,0x50)) and not callbacks and rd(u,M+8)==(0x47fb8000 if recursive else 0) and rd(u,M+4)==0 and bytes(u.mem_read(M+0x22,1))==b'\0'
 balanced(u,regs)
 results.append({'kind':'pending close defer','recursive':recursive,'page_stays_linked_and_close_flag_stays_set':True,'callback_not_called':True,'native_unlock_balanced':True,'manager_dispatch_flag_cleared_by_stock':True,'host_skip_predicate_supplied':True})
 print('PASS pending close',recursive,flush=True)
# Full worker frame plus actual dequeue/parser/comparison, two consecutive requests.
m=prepared();u=m.uc;queue_note(m,64);queue_note(m,67)
execute_until(m,0x4008b460,[],0x4008b4ae,sr=0x201f)
loopsp=u.reg_read(UC_M68K_REG_A7);q=0x40325ebc;ring=0x47fc4000;packets=[0x47fc5000,0x47fc5100]
u.mem_write(ring,u32(packets[0])+u32(packets[1])+bytes(24));u.mem_write(q+4,u32(2));u.mem_write(q+0x10,u32(7));u.mem_write(q+0x14,u32(ring));u.mem_write(q+0x1c,u32(0))
for packet,command in zip(packets,['ENTER','EXIT']):u.mem_write(packet,('#'+command+'_TEST_MODE\0').encode())
for command,boundary in [('ENTER',0x4008b85a),('EXIT',0x4008b88a)]:
 h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:u.emu_stop(),begin=boundary,end=boundary)
 u.emu_start(0x4008b4ae,0xdeadbee0,count=100000);u.hook_del(h);assert u.reg_read(UC_M68K_REG_PC)==boundary
 before=state_of(m);assert u.reg_read(UC_M68K_REG_A7)==loopsp
 textaddr=0x47fc7800;u.mem_write(textaddr,b'UNSUPPORTED: restart required\r\n\0')
 ph=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:u.mem_write(u.reg_read(UC_M68K_REG_A7),u32(textaddr)),begin=0x4008b870,end=0x4008b870)
 h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:u.emu_stop(),begin=0x4008b4ae,end=0x4008b4ae)
 u.emu_start(0x4008b86a,0xdeadbee0,count=100000);u.hook_del(h);u.hook_del(ph)
 assert before==state_of(m) and u.reg_read(UC_M68K_REG_A7)==loopsp and u.reg_read(UC_M68K_REG_PC)==0x4008b4ae

assert rd(u,q+4)==0 and rd(u,q+0x1c)==2
results.append({'kind':'two consecutive commands in real worker frame','actual_worker_initialization_dequeue_parser_comparison_printf_and_loop':True,'notification_delivery_not_certified':True,'requests_removed_once':True,'stack_balanced_across_both':True,'ring_and_packets_seeded_by_host':True,'transport_packet_ownership_not_certified':True})
print('PASS complete worker frame and two request dequeues',flush=True)
Path('outputs/Digitone-E04-PC-rejection-continuations.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_policy_installed':False,'cases':results,'limits':['Host selects rejection and supplies predicate/message; actual continuation instructions execute.','Constructed manager/list/task state, no contention or full application selector execution.','Command transport producer ownership and retry protocol not certified.','Pending close deferral clears manager dispatch flag; page remains flagged for close and retry semantics need explicit policy.','Other direct remove/destruction routes are not covered by close predicate.']},indent=2))

