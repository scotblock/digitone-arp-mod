from pathlib import Path
exec(Path('work/validate-E03-continuous-queue-action.py').read_text().split('\ntry:\n for name')[0])
r={'PC_only':True,'cases':[],'failure':None,'limits':['One persistent machine; input interleavings are explicitly scheduled at updater instruction boundaries, not delivered by real interrupts.','Stock frame dispatcher/receiver and updater execute; flash actions, registry, heap, display, locks and task scheduling retain the earlier fixtures.','Gate-disabled case uses the stock gate setter as a control; it is not a firmware modification.','No device flash or new firmware file. These tests do not establish physical reachability of the injected timing.']}
def changed_packet(index):
 b=bytearray(packets[index]);b[70]^=1;body=b[1:-1];seed=packets[0][8];b[-2]=(seed+sum(v^(seed+j) for j,v in enumerate(body[6:125])))&127;return bytes(b)
try:
 for name,target in [('baseline',None),('after_validation',0x40100460),('before_first_program',0x401004ec),('mid_program',0x401004ec),('disabled_gate_control',0x401004ec)]:
  m=make();t=time.time()
  for p in packets:m.uc.mem_write(MSG,bytes(p));call(m,0x400eaac8,[MSG,len(p),8],stack_top=STACK,limit=100000);consume(m)
  assert int.from_bytes(m.uc.mem_read(0x419950a4,4),'big')==1
  fired=[False]
  def stop(uc,pc,n,d):
   if pc==0x40100504:uc.emu_stop();return
   if fired[0]:return
   if name=='mid_program' and sum(x[0]=='program' for x in m.actions)!=50:return
   fired[0]=True;uc.emu_stop()
  handles=[m.uc.hook_add(UC_HOOK_CODE,stop,begin=0x40100504,end=0x40100504)]
  if target:handles.append(m.uc.hook_add(UC_HOOK_CODE,stop,begin=target,end=target))
  m.uc.mem_write(STACK,u32(0xdeadbee0)+u32(MAN));m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.reg_write(UC_M68K_REG_A7,STACK)
  m.uc.emu_start(0x400a8690,0xdeadbee0,count=10000000)
  case={'name':name,'target':hex(target) if target else None,'receive_gate_initially_enabled':True,'worker_entry_SR':'0x2000'}
  if target:
   assert fired[0] and m.uc.reg_read(UC_M68K_REG_PC)==target
   h=m.uc.context_save();old=bytes(m.uc.mem_read(DATA,len(wire)));prior_programs=sum(x[0]=='program' for x in m.actions)
   # Park CPU only; memory changes by stock receive routines survive context_restore.
   if name=='disabled_gate_control':call(m,0x400ed8ea,[],stack_top=STACK-0x3000,limit=1000)
   arrival=[bytes(packets[0]),changed_packet(1)]
   if name=='mid_program':arrival=[bytes(packets[0])]+[changed_packet(i) if i==140 else bytes(packets[i]) for i in range(1,146)]
   for p in arrival:m.uc.mem_write(MSG,p);call(m,0x400eaac8,[MSG,len(p),8],stack_top=STACK-0x3000,limit=100000)
   changed=bytes(m.uc.mem_read(DATA,len(wire)))!=old
   case.update(program_calls_before_interleave=prior_programs,arrival_packets=len(arrival),receive_buffer_changed=changed,receive_phase_after_arrival=m.uc.mem_read(STATE,1)[0],receive_gate_after_arrival=int.from_bytes(m.uc.mem_read(0x419950a4,4),'big'))
   assert changed==(name!='disabled_gate_control')
   m.uc.context_restore(h);m.uc.emu_start(target,0xdeadbee0,count=10000000)
  assert m.uc.reg_read(UC_M68K_REG_PC)==0x40100504
  for handle in handles:m.uc.hook_del(handle)
  expected=wire[8:8+int.from_bytes(wire[:4],'big')];written=m.flash[0x80000:0x80000+len(expected)]
  mismatches=[i for i,(a,b) in enumerate(zip(written,expected)) if a!=b]
  assert bool(mismatches)==(name in ['after_validation','before_first_program','mid_program'])
  case.update(program_calls=sum(x[0]=='program' for x in m.actions),erase_calls=sum(x[0]=='erase' for x in m.actions),programming_completed=True,flash_equals_original_completed_image=not mismatches,changed_flash_bytes=len(mismatches),first_changed_flash_offset=hex(0x80000+mismatches[0]) if mismatches else None,seconds=time.time()-t)
  assert bytes(m.uc.mem_read(0x40000400,0x18fc00))==stock[:0x18fc00]
  r['cases'].append(case);print('PASS',name,case['changed_flash_bytes'],flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-receive-buffer-interleaving-checks.json').write_text(json.dumps(r,indent=2))
