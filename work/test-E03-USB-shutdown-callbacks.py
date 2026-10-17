from pathlib import Path
exec(Path('work/test-E03-deferred-USB-freeze.py').read_text().split("\nr={'PC_only'")[0])
EP=0x80000080;DESC=0x47f30000;POOL=0x47f31000

def setup(real_release=False):
 m=make();usb_setup(m)
 if not real_release:register_release_fixture(m)
 for a in [EP,0xfc0b0000,DESC,POOL,0x40529388,0x429f23b8]:m.ensure(a)
 m.uc.mem_write(EP,bytes(128));m.uc.mem_write(0x429f23b8,bytes(4));m.uc.mem_write(0x40529258,u32(1));m.uc.mem_write(0x40529250,u32(1))
 m.uc.mem_write(0x40529388,u32(POOL));m.uc.mem_write(POOL,bytes(384))
 for n in range(5):m.uc.mem_write(POOL+n*64+0x34,u32(POOL+(n+1)*64))
 m.uc.mem_write(0xfc0b014c,u32(0));m.uc.mem_write(0xfc0b01b0,u32(2));m.uc.mem_write(0xfc0b01b4,u32(0))
 call(m,0x40001c78,[WQ,0,0x40527f5c,128],stack_top=STACK,limit=1000);m.uc.mem_write(0x40526104,u32(0))
 m.submits=[];m.callbacks=[];m.acks=0
 def observe(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7)
  if pc==0x40005f1e:m.submits.append({'endpoint':int.from_bytes(uc.mem_read(sp+4,4),'big'),'descriptor':hex(int.from_bytes(uc.mem_read(sp+8,4),'big'))})
  elif pc==0x40006070:m.submits[-1]['return']=hex(uc.reg_read(UC_M68K_REG_D0))
  elif pc==0x4000472a:m.callbacks.append(int.from_bytes(uc.mem_read(sp+4,4),'big'))
  else:uc.mem_write(0xfc0b01b4,u32(0));m.acks+=1
 for pc in [0x40005f1e,0x40006070,0x4000472a,0x4000482c,0x40004838]:m.uc.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc)
 return m

r={'PC_only':True,'cases':[],'failure':None,'limits':['Descriptor chains, completed bulk payload and free-descriptor pool are controlled fixtures. USB registers acknowledge shutdown immediately in host hooks.','Stock completion, replenish, allocator, endpoint submit, descriptor cleanup and shutdown code execute; hardware acceptance, DMA pacing and outer shutdown preconditions are not certified.','No naturally scheduled interrupt race is asserted.']}
try:
 for name in ['completion_positive','completion_zero','cleanup_positive','shutdown_positive_gate_open','shutdown_positive_gate_frozen','shutdown_submit_blocked','shutdown_real_buffer_release','shutdown_guarded_real_release']:
  guarded=name=='shutdown_guarded_real_release';real_release=name in ['shutdown_real_buffer_release','shutdown_guarded_real_release'];m=setup(real_release);buffer=0x4bc0d000 if real_release else MSG;m.ensure(buffer)
  m.guard_blocks=0
  if guarded:
   def guard(uc,pc,n,d):
    m.guard_blocks+=1;sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_PC,ret)
   m.uc.hook_add(UC_HOOK_CODE,guard,begin=0x4000465a,end=0x4000465a)
  payload=encode_usb(bytes(packets[0]))+encode_usb(changed_packet(1));m.uc.mem_write(buffer,payload);before=bytes(m.uc.mem_read(DATA,202))
  if name.endswith('gate_frozen') or guarded:call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
  if name=='shutdown_submit_blocked':m.uc.mem_write(0x429f23b8,u32(2))
  if name.startswith('completion'):
   call(m,0x4000472a,[len(payload) if name=='completion_positive' else 0,buffer],stack_top=STACK,limit=100000)
  else:
   m.uc.mem_write(DESC,bytes(64));m.uc.mem_write(DESC,u32(1));m.uc.mem_write(DESC+0x20,u32(len(payload)));m.uc.mem_write(DESC+0x24,u32(0x4000472a));m.uc.mem_write(DESC+0x30,u32(buffer));m.uc.mem_write(EP+0x30,u32(DESC));m.uc.mem_write(EP+0x34,u32(DESC))
   call(m,0x40005e42 if name=='cleanup_positive' else 0x40004806,[1] if name=='cleanup_positive' else [],stack_top=STACK,limit=100000)
  assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
  count=int.from_bytes(m.uc.mem_read(0x40529258,4),'big');head=int.from_bytes(m.uc.mem_read(EP+0x30,4),'big');queued=int.from_bytes(m.uc.mem_read(WQ+4,4),'big')
  assert len(m.submits)==(0 if guarded else 2) and queued==(0 if name=='completion_zero' else 1)
  assert count==(0 if name.startswith('shutdown') else 2)
  if not name.startswith('completion'):assert head==0
  if name=='shutdown_submit_blocked':assert all(s['return']=='0xffffffff' for s in m.submits)
  else:assert all(s['return']=='0x0' for s in m.submits)
  submissions_before_deferred=list(m.submits)
  if queued:deferred_drain(m);usb_drain(m)
  count_after_deferred=int.from_bytes(m.uc.mem_read(0x40529258,4),'big')
  if real_release and not guarded:assert len(m.submits)==4 and count_after_deferred==2 and int.from_bytes(m.uc.mem_read(EP+0x30,4),'big')!=0
  if guarded:assert len(m.submits)==0 and count_after_deferred==0 and m.guard_blocks==2 and int.from_bytes(m.uc.mem_read(EP+0x30,4),'big')==0
  changed=bytes(m.uc.mem_read(DATA,202))!=before
  assert changed==(name not in ['completion_zero','shutdown_positive_gate_frozen','shutdown_guarded_real_release'])
  r['cases'].append({'name':name,'callback_lengths':m.callbacks,'submit_attempts_before_deferred':submissions_before_deferred,'submit_attempts_total':m.submits,'outstanding_after':count,'outstanding_after_deferred':count_after_deferred,'endpoint_head_after':hex(head),'deferred_work_after':queued,'receiver_changed_after_deferred_consumption':changed,'shutdown_ack_fixture_calls':m.acks,'stock_buffer_release_executed':real_release,'host_guard_blocked_entries':m.guard_blocks})
  print('PASS shutdown',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-USB-shutdown-callback-checks.json').write_text(json.dumps(r,indent=2))
if r['failure']:raise SystemExit(1)
