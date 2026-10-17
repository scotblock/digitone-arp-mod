from pathlib import Path
exec(Path('work/test-E03-USB-shutdown-callbacks.py').read_text().split("\nr={'PC_only'")[0])

def prepared(guarded):
 m=setup(True);m.lease=guarded;m.blocks=0;m.timers=[]
 def guard(uc,pc,n,d):
  if not m.lease:return
  m.blocks+=1;sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_D0,0);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,guard,begin=0x4000465a,end=0x4000465a)
 def timer(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret,arg=struct.unpack('>II',uc.mem_read(sp,8));m.timers.append((hex(pc),hex(arg)));uc.reg_write(UC_M68K_REG_D0,0x47f32000 if pc==0x40006d68 else 0);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 for pc in [0x40006d68,0x40006dde,0x40006f22]:m.uc.hook_add(UC_HOOK_CODE,timer,begin=pc,end=pc)
 for pc in [0x400051f8,0x40005202]:m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:uc.mem_write(0xfc0b01b4,u32(1)),begin=pc,end=pc)
 m.uc.mem_write(0x40229720,u32(0xffffffff));m.ensure(0x4bc0d000)
 payload=encode_usb(bytes(packets[0]))+encode_usb(changed_packet(1));m.uc.mem_write(0x4bc0d000,payload);m.payload_length=len(payload)
 call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
 return m

def descriptor(m):
 m.uc.mem_write(DESC,bytes(64));m.uc.mem_write(DESC,u32(1));m.uc.mem_write(DESC+0x20,u32(m.payload_length));m.uc.mem_write(DESC+0x24,u32(0x4000472a));m.uc.mem_write(DESC+0x30,u32(0x4bc0d000));m.uc.mem_write(EP+0x30,u32(DESC));m.uc.mem_write(EP+0x34,u32(DESC))

def snapshot(m):
 return {'outstanding':int.from_bytes(m.uc.mem_read(0x40529258,4),'big'),'endpoint_head':hex(int.from_bytes(m.uc.mem_read(EP+0x30,4),'big')),'queued_deferred':int.from_bytes(m.uc.mem_read(WQ+4,4),'big'),'submit_attempts':len(m.submits),'guard_blocks':m.blocks,'submit_block_mask':hex(int.from_bytes(m.uc.mem_read(0x429f23b8,4),'big'))}

r={'PC_only':True,'cases':[],'failure':None,'limits':['Outer routine entries are explicitly invoked with controlled endpoint chains and register acknowledgments. Natural mode-transition eligibility and physical DMA completion remain unverified.','Timer registration/removal and unrelated task teardown are host fixtures. Lease/guard are host state.','Late callbacks are deliberately invoked probes, not proof that the stock hardware can deliver them after cancellation.']}
try:
 for entry in [0x40003a1e,0x400044ec]:
  for guarded in [False,True]:
   m=prepared(guarded);descriptor(m);before=bytes(m.uc.mem_read(DATA,202))
   call(m,entry,[],stack_top=STACK,limit=200000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   stopped=snapshot(m);assert stopped['outstanding']==0 and stopped['queued_deferred']==1
   deferred_drain(m);usb_drain(m);after=snapshot(m)
   assert bytes(m.uc.mem_read(DATA,202))==before
   assert after['submit_attempts']==(0 if guarded else 4) and after['outstanding']==(0 if guarded else 2)
   r['cases'].append({'entry':hex(entry),'guarded':guarded,'after_outer_return':stopped,'after_deferred_release':after,'receive_unchanged':True,'timer_fixtures':m.timers})
   print('PASS outer',hex(entry),guarded,flush=True)
 for kind in ['late_positive','late_zero','periodic','lease_released_before_late_positive','both_restored_before_late_positive','gate_restored_with_guard_held']:
  m=prepared(True);m.uc.mem_write(0x40529258,u32(0));before=bytes(m.uc.mem_read(DATA,202))
  call(m,0x400044ec,[],stack_top=STACK,limit=200000);stopped=snapshot(m);assert stopped['outstanding']==0 and stopped['queued_deferred']==0
  if kind in ['lease_released_before_late_positive','both_restored_before_late_positive']:m.lease=False
  if kind in ['both_restored_before_late_positive','gate_restored_with_guard_held']:call(m,0x400ed8dc,[],stack_top=STACK,limit=1000)
  if kind=='periodic':call(m,0x40004752,[],stack_top=STACK,limit=100000)
  else:call(m,0x4000472a,[0 if kind=='late_zero' else m.payload_length,0x4bc0d000],stack_top=STACK,limit=100000)
  callback=snapshot(m)
  if callback['queued_deferred']:deferred_drain(m);usb_drain(m)
  after=snapshot(m);changed=bytes(m.uc.mem_read(DATA,202))!=before
  assert changed==(kind in ['both_restored_before_late_positive','gate_restored_with_guard_held'])
  if kind=='periodic':assert after['outstanding']==0 and after['submit_attempts']==0
  elif kind in ['lease_released_before_late_positive','both_restored_before_late_positive']:assert after['submit_attempts']==3 and after['outstanding']==2
  else:assert after['outstanding']==0xffffffff and after['submit_attempts']==0
  r['cases'].append({'probe':kind,'after_outer_return':stopped,'after_callback':callback,'after_drain':after,'receive_unchanged':not changed})
  print('PASS late',kind,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-USB-outer-late-callback-checks.json').write_text(json.dumps(r,indent=2))
if r['failure']:raise SystemExit(1)
