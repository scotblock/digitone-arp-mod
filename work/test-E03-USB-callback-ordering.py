from pathlib import Path
exec(Path('work/test-E03-USB-cancellation-dispatch.py').read_text().split("\nr={'PC_only'")[0])

def register_service(m):
 m.uc.mem_write(0x40229700,u32(0));m.uc.mem_write(0x40528624,u32(0));m.uc.mem_write(0x429f21bc,bytes(192))
 def unlock(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,unlock,begin=0x40001b6e,end=0x40001b6e)
 call(m,0x40002ecc,[0x40007650,4],stack_top=STACK,limit=10000)
 node=int.from_bytes(m.uc.mem_read(0x40528624,4),'big');assert int.from_bytes(m.uc.mem_read(node,4),'big')==0x40007650 and int.from_bytes(m.uc.mem_read(node+4,4),'big')==4
 return node

def interrupt(m,return_pc,level):
 uc=m.uc;sp=uc.reg_read(UC_M68K_REG_A7)-8;uc.mem_write(sp,struct.pack('>HHI',0x4158,0x2000,return_pc));uc.reg_write(UC_M68K_REG_SR,0x2000|(level<<8));uc.reg_write(UC_M68K_REG_A7,sp)
 uc.mem_write(0x405292a8,u32(1));uc.mem_write(0xfc0b01ac,u32(0));uc.mem_write(0xfc0b01bc,u32(2));m.ensure(0xfc04c014)
 uc.emu_start(0x400073ac,return_pc,count=100000);assert uc.reg_read(UC_M68K_REG_PC)==return_pc

r={'PC_only':True,'cases':[],'failure':None,'limits':['Service registration/list traversal, cancellation processing, IRQ entry/callback and full IRQ RTE execute. Scheduler wake/locking are fixtures; task and IRQ start explicitly.','IRQ level 3 or 4 and format-4 exception frame are injected test states, not certified hardware interrupt configuration.','The probes do not model nested higher-priority interrupt handlers, real scheduler preemption or physical controller acknowledgment.']}
try:
 for level in [3,4]:
  for preempt in [False,True]:
   m=init(True);m.install_exceptions();node=register_service(m);m.order=[]
   def ordered(uc,pc,n,d):m.order.append({'pc':hex(pc),'callback_selected':hex(uc.reg_read(UC_M68K_REG_A5)) if pc==0x400075c8 else None})
   for pc in [0x400075c8,0x4000472a,0x400075d4,0x40007614,ACK]:m.uc.hook_add(UC_HOOK_CODE,ordered,begin=pc,end=pc)
   call(m,0x40005e04,[1,ACK],stack_top=STACK,limit=10000);m.uc.mem_write(0xfc0b01b4,u32(0))
   stop_pc=0x400076c4 if preempt else 0x40002ebe
   def boundary(uc,pc,n,d):
    if pc==0x400076c4 or m.notices:uc.emu_stop()
   h=m.uc.hook_add(UC_HOOK_CODE,boundary,begin=stop_pc,end=stop_pc)
   sp=STACK-0x10000;m.uc.mem_write(sp,u32(0xdeadbee0));m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.reg_write(UC_M68K_REG_A7,sp)
   m.uc.emu_start(0x40002e6e,0xdeadbee0,count=200000);assert m.uc.reg_read(UC_M68K_REG_PC)==stop_pc;m.uc.hook_del(h)
   if preempt:
    # Interrupt at a task boundary before JSR cleanup: task state is restored by stock IRQ RTE.
    interrupt(m,stop_pc,level)
    assert len(m.callbacks)==1 and not m.notices
    h=m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:uc.emu_stop(),begin=0x40002ebe,end=0x40002ebe)
    m.uc.emu_start(stop_pc,0xdeadbee0,count=100000);m.uc.hook_del(h)
    assert m.uc.reg_read(UC_M68K_REG_PC)==0x40002ebe
   assert len(m.notices)==1 and len(m.callbacks)==1 and snapshot(m)['outstanding']==0
   if preempt:
    order=[o['pc'] for o in m.order];assert order.index('0x400075c8')<order.index('0x4000472a')<order.index('0x40007614')<order.index(hex(ACK))
   # After acknowledged cleanup, actual IRQ return with an empty chain produces no old callback.
   interrupt(m,0xdeadbee0,level);assert len(m.callbacks)==1
   deferred_drain(m);usb_drain(m)
   assert snapshot(m)['outstanding']==0 and not m.submits
   r['cases'].append({'IRQ_level_fixture':level,'IRQ_preempts_cancellation_task_before_cleanup':preempt,'registered_service_node':hex(node),'callback_count':len(m.callbacks),'notification_count':len(m.notices),'order':m.order,'after_drain':snapshot(m),'empty_chain_IRQ_added_no_callback':True})
   print('PASS ordering',level,preempt,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-USB-callback-ordering-checks.json').write_text(json.dumps(r,indent=2))
if r['failure']:raise SystemExit(1)
