from pathlib import Path
exec(Path('work/test-E03-USB-outer-late-callbacks.py').read_text().split("\nr={'PC_only'")[0])
ACK=0x47f33000

def init(guarded):
 m=prepared(guarded);descriptor(m);m.notices=[];m.uc.mem_write(ACK,bytes.fromhex('4e75'))
 def ack(uc,pc,n,d):m.notices.append(snapshot(m))
 m.uc.hook_add(UC_HOOK_CODE,ack,begin=ACK,end=ACK)
 m.uc.mem_write(0x429f23c8,u32(0));m.uc.mem_write(0x405292a4,u32(0));m.uc.mem_write(0x405292a0,u32(0))
 return m

def dispatch(m):
 m.ensure(0xfc04c014);m.uc.mem_write(0x405292a8,u32(1));m.uc.mem_write(0xfc0b01ac,u32(0));m.uc.mem_write(0xfc0b01bc,u32(2))
 h=m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:uc.emu_stop(),begin=0x4000760c,end=0x4000760c)
 try:call(m,0x400073ac,[],stack_top=STACK-0x9000,limit=100000)
 finally:m.uc.hook_del(h)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0x4000760c

r={'PC_only':True,'cases':[],'failure':None,'limits':['Controller event and cancellation acknowledgment registers are host fixtures. Interrupt entry executes stock code but stops before register restore/RTE; exception delivery/priorities are not modeled.','Descriptor and timer/task fixtures from earlier tests remain. Lease and notification callback are host-only.','Completion events are explicit controls, not evidence of physical events after cancellation.']}
try:
 for name in ['cancel_pending','cancel_ack_unguarded','cancel_ack_guarded','completion_during_cancel_pending','completion_after_cancel_ack','empty_head_completion','cancel_active_descriptor','completion_active_pending','two_completed_descriptors']:
  guarded=name!='cancel_ack_unguarded';m=init(guarded);before=bytes(m.uc.mem_read(DATA,202))
  if name=='empty_head_completion':m.uc.mem_write(EP+0x30,u32(0));m.uc.mem_write(EP+0x34,u32(0));m.uc.mem_write(0x40529258,u32(0));dispatch(m)
  else:
   if name=='two_completed_descriptors':
    m.uc.mem_write(DESC+64,bytes(m.uc.mem_read(DESC,64)));m.uc.mem_write(DESC,u32(DESC+64));m.uc.mem_write(EP+0x34,u32(DESC+64));m.uc.mem_write(0x40529258,u32(2))
   if name in ['cancel_active_descriptor','completion_active_pending']:m.uc.mem_write(DESC+4,u32(0x80))
   call(m,0x40005e04,[1,ACK],stack_top=STACK,limit=10000)
   assert int.from_bytes(m.uc.mem_read(0x429f23b8,4),'big')==2 and int.from_bytes(m.uc.mem_read(0x429f23c8,4),'big')==2
   if name=='completion_during_cancel_pending':dispatch(m);assert len(m.callbacks)==1
   if name=='completion_active_pending':dispatch(m);assert not m.callbacks
   if name not in ['cancel_pending','completion_active_pending']:m.uc.mem_write(0xfc0b01b4,u32(0))
   call(m,0x40007650,[],stack_top=STACK,limit=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   if name in ['completion_after_cancel_ack','two_completed_descriptors']:dispatch(m)
  after=snapshot(m);pending=int.from_bytes(m.uc.mem_read(0x429f23c8,4),'big');callbacks=len(m.callbacks)
  if name in ['cancel_pending','completion_active_pending']:assert pending==2 and after['submit_block_mask']=='0x2' and callbacks==0 and not m.notices
  elif name=='empty_head_completion':assert callbacks==0 and after['outstanding']==0
  elif name=='cancel_active_descriptor':assert pending==0 and after['submit_block_mask']=='0x0' and callbacks==0 and after['outstanding']==1 and len(m.notices)==1 and m.notices[0]['queued_deferred']==0 and after['endpoint_head']=='0x0'
  else:
   expected_callbacks=2 if name=='two_completed_descriptors' else 1
   assert pending==0 and after['submit_block_mask']=='0x0' and len(m.notices)==1 and callbacks==expected_callbacks
   assert m.notices[0]['submit_block_mask']=='0x0' and m.notices[0]['queued_deferred']==expected_callbacks
   assert after['outstanding']==(2 if name=='cancel_ack_unguarded' else 0)
   assert after['submit_attempts']==(2 if name=='cancel_ack_unguarded' else 0)
   if name=='cancel_ack_unguarded':assert all(s['return']=='0xffffffff' for s in m.submits)
  if after['queued_deferred']:deferred_drain(m);usb_drain(m)
  assert bytes(m.uc.mem_read(DATA,202))==before
  r['cases'].append({'name':name,'after_dispatch':after,'pending_mask':hex(pending),'callback_count':callbacks,'completion_notifications':m.notices,'after_deferred_drain':snapshot(m),'receiver_unchanged':True})
  print('PASS cancellation',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-USB-cancellation-dispatch-checks.json').write_text(json.dumps(r,indent=2))
if r['failure']:raise SystemExit(1)
