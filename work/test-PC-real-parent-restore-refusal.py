from pathlib import Path
exec(Path('work/test-PC-stock-audio-restoration.py').read_text().split('\nfor recursive in [False,True]:')[0])
results=[]
def fixture(recursive):
 m=prepared();u=m.uc;A=call(m,0x400e96c0,[0x248],stack_top=RESETSTACK,limit=100000);call(m,0x400b2b5e,[A],stack_top=RESETSTACK,limit=2000000);P=A+0x38;O=call(m,0x400e96c0,[0x2cc],stack_top=RESETSTACK,limit=100000)
 execute_until(m,0x40072a7e,[O],0x40072ac4,sr=0x201f);PP=O+0x38
 parent_callbacks=[rd(u,a+12) for a in range(rd(u,PP+0x34),rd(u,PP+0x38),16)];assert parent_callbacks==[0x400e47ae]
 M=0x47fb0000;TASK=M+0x8000;H=M+0x6000
 for a in [M,TASK,H]:m.ensure(a)
 u.mem_write(M,bytes(0x100));u.mem_write(M+20,u32(M+20)+u32(M+20));u.mem_write(0x429f2188,u32(TASK))
 if recursive:u.mem_write(M+8,u32(TASK))
 u.reg_write(UC_M68K_REG_A0,H);call(m,0x400e43fc,[O,P],stack_top=RESETSTACK,limit=100000);C=rd(u,H+4);call(m,0x401774c0,[O+0x8c,H],stack_top=RESETSTACK,limit=100000)
 app=call(m,0x4014a060,[],stack_top=RESETSTACK,limit=1000000);queue_note(m,64);queue_note(m,67)
 return m,M,TASK,H,A,P,O,PP,C,app,parent_callbacks

def registry(u,app):
 begin=rd(u,app+0x198);end=rd(u,app+0x19c);cap=rd(u,app+0x1a0)
 assert begin<=end<=cap and (end-begin)%4==0
 return {'begin':begin,'end':end,'capacity':cap,'entries':[rd(u,a) for a in range(begin,end,4)]}
for when,stop in [('before_parent_callbacks',0x400e4e2e),('after_parent_callbacks_before_transfer',0x400e4e42)]:
 for recursive in [False,True]:
  m,M,TASK,H,A,P,O,PP,C,app,cbs=fixture(recursive);u=m.uc;before=state_of(m);refs=bytes(u.mem_read(O+0x84,16))+bytes(u.mem_read(C,16));page=bytes(u.mem_read(PP,0x34));rb=registry(u,app);parent=[];child=[];regs=saved(u)
  h=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:parent.append(hex(pc)),begin=0x400aedc2,end=0x400aedc2)
  h2=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:child.append(hex(pc)),begin=0x400e7e7e,end=0x400e7e7e)
  execute_until(m,0x400e4e1e,[O,M],stop,sr=0x201f);u.emu_start(0x400e4eae,0xdeadbee0,count=100000)
  u.hook_del(h);u.hook_del(h2);balanced(u,regs);ra=registry(u,app)
  assert before==state_of(m) and refs==bytes(u.mem_read(O+0x84,16))+bytes(u.mem_read(C,16)) and not child and rd(u,M+8)==(TASK if recursive else 0) and rd(u,M+4)==0
  if when=='before_parent_callbacks':assert not parent and rb==ra and page==bytes(u.mem_read(PP,0x34))
  else:assert len(parent)==1 and ra['entries']==rb['entries']+[PP] and rd(u,PP+0x2c)==M and bytes(u.mem_read(PP+0x14,1))==b'\1'
  results.append({'when':when,'recursive':recursive,'stock_audio_constructor_completed':True,'actual_settings_base_parent_prefix_executed':True,'parent_entry_callbacks':[hex(v) for v in cbs],'parent_registry_callback_executions':parent,'registry_before':rb,'registry_after':ra,'child_audio_entry_not_called':True,'selected_retained_refs_and_counts_preserved':True,'audio_vector_queue_pool_context_gates_preserved':True,'native_return_registers_stack_and_mutex_state_balanced':True,'host_refusal_tail_selected':True,'whole_outer_parent_transition_veto_proven':False})
  print('PASS refusal',when,recursive,'registry_callback',len(parent),flush=True)
Path('outputs/Digitone-E04-PC-real-parent-restore-refusal.json').write_text(json.dumps({'PC_only':True,'passed':True,'native_guard_installed':False,'cases':results,'limits':['Settings construction executes only through its base-parent return; full settings constructor hits an uninitialized application dependency at 400634ec in this snapshot.','Audio child fully stock-constructed; parent entry records come from actual settings constructor prefix, not supplied callbacks.','Outer manager publication/caller return semantics, full exit/reinitialization dispatch, live concurrency and hardware behavior unproven.','Host supplies refusal and initial retained child assignment; no machine-code guard installed.']},indent=2))
