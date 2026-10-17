from pathlib import Path
exec(Path('work/test-PC-computed-selection-controls.py').read_text().split('\nfor recursive in [False,True]:')[0])
results=[]
original_call=call
def call(m,func,args,**kw):
 result=original_call(m,func,args,**kw)
 assert m.uc.reg_read(UC_M68K_REG_PC)==kw.get('ret_magic',0xdeadbee0),(hex(func),hex(m.uc.reg_read(UC_M68K_REG_PC)))
 if kw.get('stack_top') is not None:assert m.uc.reg_read(UC_M68K_REG_A7)==kw['stack_top']+4
 return result
for recursive in [False,True]:
 m=prepared();u=m.uc;A=call(m,0x400e96c0,[0x248],stack_top=RESETSTACK,limit=100000);call(m,0x400b2b5e,[A],stack_top=RESETSTACK,limit=2000000);P=A+0x38
 factory=prepared;prepared=lambda:m
 try:m,M,N,placeholder,C,H=setup(recursive,0x401e197a)
 finally:prepared=factory
 assert rd(u,A)==0x401c467c and rd(u,P)==0x401c4714 and rd(u,P+0x28)==0x401e197a
 O,Q,D,CL=owner(m,M,P,C);u.mem_write(O+0x38,u32(0x401a3530));u.mem_write(M+20,u32(M+20)+u32(M+20))
 # Actual settings-style wrapper builds ownership and registers its clear closure.
 u.reg_write(UC_M68K_REG_A0,H);call(m,0x400e43fc,[O,P],stack_top=RESETSTACK,limit=100000);C=rd(u,H+4);assert rd(u,H)==P and rd(u,C+4)==1
 call(m,0x401774c0,[O+0x84,H],stack_top=RESETSTACK,limit=100000);assert rd(u,C+4)==2 and rd(u,D+4)==1
 regs=saved(u);execute_until(m,0x400e4ec2,[O],0x400e4ef8,sr=0x201f);u.emu_start(0x400e4ef8,0xdeadbee0,count=100000);balanced(u,regs)
 assert bytes(u.mem_read(O+0x8c,8))==u32(P)+u32(C) and rd(u,C+4)==3
 clear_records=[]
 for at in range(rd(u,P+0x40),rd(u,P+0x44),16):
  if rd(u,at+12)==0x400e4848:clear_records.append(at)
 assert len(clear_records)==1;clear_data=rd(u,clear_records[0]);assert rd(u,clear_data)==O
 # Invoke only the actual registered clear target; full exit dispatch would
 # also run the separate diagnostic setup/reset callback and is outside this test.
 call(m,0x400e4848,[clear_records[0]],stack_top=RESETSTACK,limit=100000);assert bytes(u.mem_read(O+0x84,8))==bytes(8) and rd(u,C+4)==2
 before=state_of(m);helpers=[];entries=[];alloc=[];writes=[];entry_bodies=[]
 h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:helpers.append(pc),begin=0x400e47e6,end=0x400e47e6)
 h2=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:entries.append(hex(pc)),begin=0x400b25bc,end=0x400b25bc)
 h4=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:entry_bodies.append(hex(pc)),begin=0x400e7e7e,end=0x400e7e7e)
 h3=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:alloc.append(rd(u,u.reg_read(UC_M68K_REG_A7)+4)),begin=0x400e96c0,end=0x400e96c0)
 regs=saved(u);state=execute_until(m,0x400e4e1e,[O,M],0x400b25bc,sr=0x201f)
 assert not helpers and bytes(u.mem_read(O+0x84,8))==u32(P)+u32(C) and bytes(u.mem_read(O+0x8c,8))==bytes(8)
 resume(m,state,0xdeadbee0)
 for hh in [h,h2,h3,h4]:u.hook_del(hh)
 balanced(u,regs);after=state_of(m);print('RESTORE',recursive,'entry',entries,'alloc',alloc,'before',before['audio_vector'],'after',after['audio_vector'],flush=True)
 assert not helpers and len(entries)==2 and len(entry_bodies)==1 and before['audio_vector']!=after['audio_vector'] and all(before[k]==after[k] for k in before if k!='audio_vector')
 node=rd(u,M+20);assert node!=M+20 and rd(u,node+8)==P and rd(u,P+0x2c)==M and rd(u,C+4)==3 and rd(u,D+4)==1 and rd(u,M+8)==(M+0x8000 if recursive else 0) and rd(u,M+4)==0
 results.append({'recursive':recursive,'stock_heap_audio_root':hex(A),'stock_constructor_completed':True,'real_audio_name_and_vtables':True,'entry_callback_boundary_observations':entries,'entry_body_executions':entry_bodies,'native_settings_style_ownership_wrapper':True,'saved_reference_guest_produced':True,'actual_registered_clear_target_executed':True,'raw_allocator_entry_observations':alloc,'audio_vector_before':before['audio_vector'],'audio_vector_after':after['audio_vector'],'restore_and_entry_completed':True,'shared_helper_bypassed':True,'node_published_and_page_bound':True,'temporary_refs_and_mutex_balanced':True,'note_state_pool_and_context_preserved':True,'initial_selection_supplied_by_host_through_native_assignment':True,'full_exit_dispatch_not_executed':True})
Path('outputs/Digitone-E04-PC-stock-audio-restoration.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'cases':results,'limits':['Parent/list/current-task state and initial selection constructed; native ownership wrapper creates control block and registers clear callback.','Actual audio page constructor, wrapper, save and registered clear target, restoration entry callbacks, manager, render, allocator and cleanup execute. Full diagnostic exit callback dispatch is not executed.','Full hardware startup, original audio-selection request and live concurrency not established.','Parent/list state is constructed; parent entry callback list is empty. Audio child entry records come from the actual constructor.','Entry callback boundary appears twice because the test pauses there and resumes at the same address; entry body executes once. Raw allocator observations may include lazy mapping retries.']},indent=2))
