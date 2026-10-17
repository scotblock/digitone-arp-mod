from pathlib import Path
exec(Path('work/test-PC-removal-bypass-controls.py').read_text().split('\nfor recursive in [False,True]:')[0])
results=[]
def owner(m,M,P,C):
 u=m.uc;O=M+0x7000;Q=M+0xa000;D=M+0xb000;CL=M+0xc000;X=M+0xd000
 for a in [O,Q,D,CL,X]:m.ensure(a)
 u.mem_write(O,bytes(0x400));u.mem_write(Q,bytes(0x60));u.mem_write(D,u32(0x40192020)+u32(2)+u32(2)+u32(Q));u.mem_write(O+0x64,u32(M));u.mem_write(O+0x84,u32(Q)+u32(D));u.mem_write(CL,u32(X));u.mem_write(X,u32(O));return O,Q,D,CL
for recursive in [False,True]:
 # Negative control: manager denies, but the outer helper already updated parent.
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;O,Q,D,CL=owner(m,M,P,C);before=state_of(m);manager=bytes(u.mem_read(M+20,16));audio=[];regs=saved(u)
 h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:audio.append(pc),begin=0x400b25bc,end=0x400b25bc)
 execute_until(m,0x400e47e6,[O,H],0x400e637c,sr=0x201f)
 assert bytes(u.mem_read(O+0x84,8))==u32(P)+u32(C) and rd(u,C+4)==4 and rd(u,D+4)==1
 u.reg_write(UC_M68K_REG_D2,0);u.emu_start(0x400e649a,0xdeadbee0,count=100000);u.hook_del(h)
 balanced(u,regs);assert u.reg_read(UC_M68K_REG_D0)&255==0 and before==state_of(m) and manager==bytes(u.mem_read(M+20,16)) and rd(u,C+4)==3 and rd(u,D+4)==1 and not audio
 results.append({'kind':'manager-only denial negative control','recursive':recursive,'false_return_propagates_from_shared_helper':True,'parent_selected_reference_already_changed':True,'old_strong_owner_released_new_owner_retained':True,'note_pool_context_and_manager_list_preserved':True,'audio_entry_not_called':True,'audio_reference_supplied_directly_by_host_not_actual_request':True});print('PASS manager-only negative',recursive,flush=True)
 # Proposed earlier helper refusal, before its assignment call.
 m,M,N,P,C,H=setup(recursive,0x401e197a);u=m.uc;O,Q,D,CL=owner(m,M,P,C);before=state_of(m);selected=bytes(u.mem_read(O+0x84,8));refs=bytes(u.mem_read(C,16))+bytes(u.mem_read(D,16));manager=bytes(u.mem_read(M+20,16));regs=saved(u)
 execute_until(m,0x400e47e6,[O,H],0x400e47f6,sr=0x201f);u.reg_write(UC_M68K_REG_D0,0);u.emu_start(0x400e483c,0xdeadbee0,count=100000)
 balanced(u,regs);assert u.reg_read(UC_M68K_REG_D0)==0 and before==state_of(m) and selected==bytes(u.mem_read(O+0x84,8)) and refs==bytes(u.mem_read(C,16))+bytes(u.mem_read(D,16)) and manager==bytes(u.mem_read(M+20,16))
 results.append({'kind':'earlier shared-helper refusal','recursive':recursive,'native_restore_return_tail_balanced':True,'selected_reference_ownership_and_note_state_preserved':True,'host_false_result_and_tail_selected':True,'actual_audio_selection_request_unidentified':True});print('PASS early helper denial',recursive,flush=True)
menu=json.loads(Path('outputs/Digitone-E04-PC-audio-selection-menu-map.json').read_text())
for r in menu['callbacks']:
 m,M,N,P,C,H=setup(False,int(r['label_address'],16));u=m.uc;O,Q,D,CL=owner(m,M,P,C);off=int(r['child_offset'],16);u.mem_write(O+off,u32(P)+u32(C));u.mem_write(O+0x2b4,u32(Q)+u32(D));before=state_of(m);audio_reads=[];hits=[];regs=saved(u)
 from unicorn import UC_HOOK_MEM_READ
 h=u.hook_add(UC_HOOK_MEM_READ,lambda u,ac,a,n,v,d:audio_reads.append(hex(a)),begin=O+0x2b4,end=O+0x2bb)
 def deny(u,pc,n,d):hits.append(hex(pc));u.reg_write(UC_M68K_REG_D2,0);u.reg_write(UC_M68K_REG_PC,0x400e649a)
 h2=u.hook_add(UC_HOOK_CODE,deny,begin=0x400e637c,end=0x400e637c)
 fn=int(r['callback'],16);ret=fn+0x44 if fn!=0x40072560 else 0x400725ac
 execute_until(m,fn,[CL],ret,sr=0x201f);u.emu_start(ret,0xdeadbee0,count=10);u.hook_del(h);u.hook_del(h2)
 balanced(u,regs);assert before==state_of(m) and len(hits)==1 and not audio_reads and bytes(u.mem_read(O+0x2b4,8))==u32(Q)+u32(D)
 ordinary=r['selector']=='0x400e47e6';assert bytes(u.mem_read(O+0x84,8))==(u32(P)+u32(C) if ordinary else u32(Q)+u32(D)) and rd(u,C+4)==(3 if ordinary else 2) and rd(u,D+4)==(1 if ordinary else 2)
 results.append({'kind':'registered menu callback execution','label':r['label'],'callback':r['callback'],'child_offset':r['child_offset'],'selector':r['selector'],'audio_slot_not_read':True,'callback_does_not_branch_on_selection_result':True,'parent_selection_changes_under_manager_denial':ordinary,'native_temporary_reference_cleanup_balanced':True,'controlled_page_and_slot_fixtures':True});print('PASS menu callback',r['label'],flush=True)
Path('outputs/Digitone-E04-PC-audio-selection-controls.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'actual_audio_selection_caller_identified':False,'cases':results,'limits':['Native helpers and registered callbacks execute with constructed parent/child/control/task state.','Host supplies manager/helper rejection; no installed machine-code enforcement.','Audio-reference helper tests supply that reference directly; they do not establish an actual application request.','Menu creation/dispatch and computed diagnostic selectors remain unexecuted.']},indent=2))
