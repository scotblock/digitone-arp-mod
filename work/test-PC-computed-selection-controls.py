from pathlib import Path
exec(Path('work/test-PC-audio-selection-controls.py').read_text().split('\nfor recursive in [False,True]:')[0])
results=[]
for recursive in [False,True]:
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;O,Q,D,CL=owner(m,M,P,C);u.mem_write(O+0x84,u32(P)+u32(C));u.mem_write(O+0x38,u32(0x401a3530));before=state_of(m)
 # Actual generic parent close: preserve selected ref, request child close,
 # then request parent close; no fabricated saved-slot assignment.
 regs=saved(u);execute_until(m,0x400e4ec2,[O],0x400e4ef8,sr=0x201f);u.emu_start(0x400e4ef8,0xdeadbee0,count=100000)
 balanced(u,regs);assert before==state_of(m) and bytes(u.mem_read(O+0x8c,8))==u32(P)+u32(C) and rd(u,C+4)==3
 # Actual registered closure target clears parent's selected reference.
 regs=saved(u);execute_until(m,0x400e4848,[CL],0x400e487c,sr=0x201f);u.emu_start(0x400e487c,0xdeadbee0,count=10)
 balanced(u,regs);assert bytes(u.mem_read(O+0x84,8))==bytes(8) and rd(u,C+4)==2
 # Restore handler invokes manager directly. Host supplies the established
 # false continuation at manager boundary; actual reference cleanup executes.
 helper=[];h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:helper.append(pc),begin=0x400e47e6,end=0x400e47e6)
 regs=saved(u);execute_until(m,0x400e4e1e,[O,M],0x400e637c,sr=0x201f)
 assert bytes(u.mem_read(O+0x84,8))==u32(P)+u32(C) and bytes(u.mem_read(O+0x8c,8))==bytes(8) and rd(u,C+4)==3
 u.reg_write(UC_M68K_REG_D2,0);u.emu_start(0x400e649a,0xdeadbee0,count=100000);u.hook_del(h)
 balanced(u,regs);assert before==state_of(m) and not helper and rd(u,C+4)==2 and bytes(u.mem_read(O+0x84,8))==u32(P)+u32(C) and bytes(u.mem_read(O+0x8c,8))==bytes(8)
 results.append({'kind':'native close/save, closure clear, restore/manager-deny sequence','recursive':recursive,'saved_reference_guest_produced':True,'selected_clear_guest_executed':True,'restore_bypasses_shared_selection_helper':True,'denial_leaves_selected_restored_and_saved_empty':True,'temporary_ownership_and_mutex_balanced':True,'note_state_pool_and_context_preserved':True,'initial_audio_selection_host_seeded':True,'closure_target_directly_invoked_not_actual_dispatch':True});print('PASS native retain/clear/restore',recursive,flush=True)
 # Earlier restore refusal before saved-state transfer (parent entry prefix
 # has already run; does not certify rejecting the full parent transition).
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;O,Q,D,CL=owner(m,M,P,C);u.mem_write(O+0x38,u32(0x401a3530));u.mem_write(O+0x8c,u32(P)+u32(C));before=state_of(m);refs=bytes(u.mem_read(C,16))+bytes(u.mem_read(D,16));selected=bytes(u.mem_read(O+0x84,16));regs=saved(u)
 execute_until(m,0x400e4e1e,[O,M],0x400e4e42,sr=0x201f);u.emu_start(0x400e4eae,0xdeadbee0,count=100000)
 balanced(u,regs);assert before==state_of(m) and selected==bytes(u.mem_read(O+0x84,16)) and refs==bytes(u.mem_read(C,16))+bytes(u.mem_read(D,16))
 results.append({'kind':'early local restore defer','recursive':recursive,'selected_and_saved_references_preserved':True,'native_return_tail_balanced':True,'host_tail_selected':True,'parent_entry_prefix_executed_with_empty_callback_list':True,'whole_parent_transition_veto_unproven':True});print('PASS local restore defer',recursive,flush=True)
Path('outputs/Digitone-E04-PC-computed-selection-controls.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'actual_initial_audio_selection_identified':False,'cases':results,'limits':['Initial audio selection and parent/page/list/reference/task state constructed.','Native save/clear/restore and reference cleanup execute; clear closure target invoked directly.','Host supplies rejection branches; actual parent selection/close dispatch and nonempty parent entry callbacks unexecuted.','Computed aliases and on-device startup/restoration remain unproven.']},indent=2))
