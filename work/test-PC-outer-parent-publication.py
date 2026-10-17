from pathlib import Path
exec(Path('work/test-PC-real-parent-restore-refusal.py').read_text().split('\nfor when,stop in')[0])
results=[]
for mode in ['entry_before_callbacks','defer_child_after_callbacks','manager_before_publication']:
 for recursive in [False,True]:
  m,M,TASK,H,A,P,O,PP,C,app,cbs=fixture(recursive);u=m.uc;PH=M+0x6100;m.ensure(PH);u.reg_write(UC_M68K_REG_A0,PH);call(m,0x400e43fc,[app,PP],stack_top=RESETSTACK,limit=100000);PCONT=rd(u,PH+4);assert rd(u,PCONT+4)==1
  before=state_of(m);refs=bytes(u.mem_read(O+0x84,16))+bytes(u.mem_read(C,16));rb=registry(u,app);parent=[];child=[];snapshots=[];regs=saved(u)
  h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:parent.append(hex(pc)),begin=0x400aedc2,end=0x400aedc2)
  h2=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:child.append(hex(pc)),begin=0x400e7e7e,end=0x400e7e7e)
  stop={'entry_before_callbacks':0x400e4e2e,'defer_child_after_callbacks':0x400e4e42,'manager_before_publication':0x400e637c}[mode]
  state=execute_until(m,0x400e6352,[M,PH,0],stop,sr=0x201f)
  node_at_stop=rd(u,M+20);snapshots.append({'node':hex(node_at_stop),'page_bound_manager':hex(rd(u,PP+0x2c)),'parent_strong_count':rd(u,PCONT+4),'registry':registry(u,app)})
  if mode=='manager_before_publication':u.reg_write(UC_M68K_REG_D2,0);start=0x400e649a
  else:start=0x400e4eae
  u.emu_start(start,0xdeadbee0,count=200000);u.hook_del(h);u.hook_del(h2);balanced(u,regs);ra=registry(u,app);node=rd(u,M+20);result=u.reg_read(UC_M68K_REG_D0)&255
  assert before==state_of(m) and refs==bytes(u.mem_read(O+0x84,16))+bytes(u.mem_read(C,16)) and not child and rd(u,M+8)==(TASK if recursive else 0) and rd(u,M+4)==0
  if mode=='manager_before_publication':assert node==M+20 and result==0 and rb==ra and rd(u,PCONT+4)==1
  else:
   assert node!=M+20 and rd(u,node+8)==PP and result==1 and rd(u,PCONT+4)==2
   if mode=='entry_before_callbacks':assert not parent and rb==ra and rd(u,PP+0x2c)==0
   else:assert len(parent)==1 and ra['entries']==rb['entries']+[PP] and rd(u,PP+0x2c)==M
  results.append({'mode':mode,'recursive':recursive,'pre_refusal_publication':snapshots,'manager_return':result,'parent_node_published_after_return':node!=M+20,'parent_page_bound_after_return':hex(rd(u,PP+0x2c)),'parent_registry_callback':parent,'registry_before':rb,'registry_after':ra,'selected_and_retained_child_refs_preserved':True,'audio_entry_suppressed_and_note_state_preserved':True,'native_outer_manager_cleanup_balanced':True,'host_refusal_continuation_supplied':True})
  print('PASS outer',mode,recursive,'manager_result',result,flush=True)
# Actual application's shared-reference wrapper propagates the manager result.
for mode in ['defer_child_after_callbacks','manager_before_publication']:
 for recursive in [False,True]:
  m,M,TASK,H,A,P,O,PP,C,app,cbs=fixture(recursive);u=m.uc;PH=M+0x6100;m.ensure(PH);u.reg_write(UC_M68K_REG_A0,PH);call(m,0x400e43fc,[app,PP],stack_top=RESETSTACK,limit=100000);PCONT=rd(u,PH+4)
  AP=M-0x40;m.ensure(AP);u.mem_write(AP,bytes(0x40));u.mem_write(0x419f0e50,u32(AP));before=state_of(m);rb=registry(u,app);regs=saved(u)
  stop=0x400e4e42 if mode=='defer_child_after_callbacks' else 0x400e637c
  execute_until(m,0x40017f46,[AP,PH,0],stop,sr=0x201f)
  if mode=='manager_before_publication':u.reg_write(UC_M68K_REG_D2,0);start=0x400e649a
  else:start=0x400e4eae
  u.emu_start(start,0xdeadbee0,count=200000);balanced(u,regs);result=u.reg_read(UC_M68K_REG_D0)&255
  assert result==int(mode=='defer_child_after_callbacks') and before==state_of(m) and rd(u,PCONT+4)==(2 if result else 1) and rd(u,M+8)==(TASK if recursive else 0) and rd(u,M+4)==0
  if result:assert registry(u,app)['entries']==rb['entries']+[PP] and rd(u,PP+0x2c)==M and rd(u,M+20)!=M+20
  else:assert registry(u,app)==rb and rd(u,M+20)==M+20
  results.append({'mode':'actual_application_wrapper_'+mode,'recursive':recursive,'wrapper_entry':'0x40017f46','manager_result_propagated':result,'temporary_ref_copy_release_balanced':True,'parent_published':bool(result),'child_not_restored':bytes(u.mem_read(O+0x84,8))==bytes(8),'retained_reference_kept':bytes(u.mem_read(O+0x8c,8))==u32(P)+u32(C),'note_state_preserved':True,'native_caller_and_manager_executed':True,'application_manager_pointer_controlled':True,'host_refusal_supplied':True})
  print('PASS actual caller',mode,recursive,'result',result,flush=True)
Path('outputs/Digitone-E04-PC-outer-parent-publication.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'cases':results,'limits':['Stock audio constructor and settings base-parent prefix; full settings construction incomplete.','Manager/list/task fixtures and initial retained child selection controlled; actual outer manager executes.','Host supplies rejection/defer; no native guard installed.','Other callers, live concurrency, complete parent rendering/workloads and hardware behavior not certified.']},indent=2))
