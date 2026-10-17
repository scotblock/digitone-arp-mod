from pathlib import Path
exec(Path('work/test-PC-ui-defer-overlay.py').read_text().split('\nresults=[]')[0])
results=[]
def invoke(m,fn,args):
 u=m.uc;regs=saved(u);u.mem_write(0x47fdff00,u32(0xdeadbee0)+b''.join(u32(x) for x in args));u.reg_write(UC_M68K_REG_SR,0x201f);u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.emu_start(fn,0xdeadbee0,count=500000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0;balanced(u,regs);return u.reg_read(UC_M68K_REG_D0)&255
for recursive in [False,True]:
 seed=prepared();real_task=rd(seed.uc,0x429f2188);factory=prepared;prepared=lambda:seed
 try:m,M,TASK,H,A,P,O,PP,C,app,cbs=fixture(recursive)
 finally:prepared=factory
 u=m.uc;TASK=real_task;u.mem_write(0x429f2188,u32(TASK));u.mem_write(M+8,u32(TASK if recursive else 0));R=M+0x7000;PH=H+0x80;m.ensure(R);u.mem_write(R,bytes(0x200));u.reg_write(UC_M68K_REG_A0,PH);call(m,0x400e43fc,[R,PP],stack_top=RESETSTACK,limit=100000);PCONT=rd(u,PH+4);install(m,True)
 baseline=state_of(m);rb=registry(u,app);hits=[];hooks=[]
 for pc in [0x400e47ca,0x400e4848,0x400b25c2,0x400e7e7e,ENTRY]:hooks.append(u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:hits.append(hex(pc)),begin=pc,end=pc))
 stages=[]
 for cycle in range(3):
  invoke(m,0x401774c0,[R+0x84,PH]);assert rd(u,PCONT+4)==2
  assert invoke(m,0x400e6352,[M,PH,0])==1
  assert state_of(m)==baseline and rd(u,C+4)==2 and rd(u,PCONT+4)==3 and registry(u,app)['entries']==rb['entries']+[PP] and rd(u,PP+0x2c)==M and bytes(u.mem_read(O+0x84,8))==bytes(8) and bytes(u.mem_read(O+0x8c,8))==u32(P)+u32(C)
  stages.append({'cycle':cycle,'stage':'entered_deferred','audio_strong':rd(u,C+4),'parent_strong':rd(u,PCONT+4),'registry':registry(u,app)})
  invoke(m,0x400e4ec2,[O]);assert bytes(u.mem_read(PP+0x30,1))==b'\1'
  invoke(m,0x400e6634,[M])
  assert state_of(m)==baseline and rd(u,C+4)==2 and rd(u,PCONT+4)==1 and registry(u,app)==rb and rd(u,PP+0x2c)==0 and rd(u,M+20)==M+20 and rd(u,M+24)==M+20 and bytes(u.mem_read(R+0x84,8))==bytes(8) and bytes(u.mem_read(O+0x8c,8))==u32(P)+u32(C)
  assert rd(u,M+8)==(TASK if recursive else 0) and rd(u,M+4)==0
  stages.append({'cycle':cycle,'stage':'closed_removed','audio_strong':rd(u,C+4),'parent_strong':rd(u,PCONT+4),'registry':registry(u,app)})
 # Last parent owner release drops retained child ownership. Last audio
 # handle release runs actual virtual destructors and stock heap free.
 freed=[];fh=u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:freed.append(rd(u,u.reg_read(UC_M68K_REG_A7)+4)),begin=0x400e96cc,end=0x400e96cc)
 Z=H+0x100;m.ensure(Z);u.mem_write(Z,bytes(8))
 invoke(m,0x40158b82,[PH,Z]);assert bytes(u.mem_read(PH,8))==bytes(8) and rd(u,C+4)==1 and O in freed and state_of(m)==baseline and registry(u,app)==rb
 stages.append({'stage':'last_parent_owner_released','retained_audio_strong':rd(u,C+4),'parent_root_freed':True})
 invoke(m,0x40158b82,[H,Z]);assert bytes(u.mem_read(H,8))==bytes(8) and A in freed and C in freed and state_of(m)==baseline and registry(u,app)==rb
 stages.append({'stage':'last_audio_owner_released','audio_root_and_control_freed':True})
 u.hook_del(fh)
 for h in hooks:u.hook_del(h)
 assert hex(0x400e47ca) in hits and hex(0x400e4848) in hits and all(hex(pc) not in hits for pc in [0x400b25c2,0x400e7e7e,ENTRY])
 results.append({'recursive':recursive,'cycles':3,'stages':stages,'actual_callback_dispatch':hits,'retained_audio_never_consumed':True,'audio_entry_exit_and_pool_rebuild_not_reached':True,'parent_owners_return_to_handle_only_on_close':True,'native_list_unlink_free_registry_remove_and_wrapper_clear_execute':True,'note_state_context_audio_vector_preserved':True,'host_branch_injection':False,'outer_owner_selected_reference_fixture':True,'snapshot_current_task_identity':hex(TASK),'last_parent_and_audio_release_native_destructors_and_free':True});print('PASS deferred lifecycle',recursive,flush=True)
Path('outputs/Digitone-E04-PC-deferred-page-lifecycle.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':results,'persistent_latch_installed':False,'limits':['Outer owner is a constructed selected-reference container; actual wrapper callbacks operate on its valid owning slot. Current task identity uses the original snapshot task so inherited mutex owners remain consistent.','Parent uses stock base-constructor prefix, child full stock constructor; initial retained child state supplied.','Native manager, complete parent exit callback dispatch, reference cleanup and re-entry execute with the disposable guard.','Final shared owners are released through native assignment/destructors; test does not access freed control blocks afterward.','No live IRQ concurrency, hardware behavior or persistent admission certification.']},indent=2))
