from pathlib import Path
exec(Path('work/test-E03-USB-bulk-freeze.py').read_text().split("\nr={'PC_only'")[0])
WQ=0x4052815c

def deferred_drain(m):
 def idle(uc,pc,n,d):
  if int.from_bytes(uc.mem_read(WQ+4,4),'big')==0:uc.emu_stop()
 h=m.uc.hook_add(UC_HOOK_CODE,idle,begin=0x400012ec,end=0x400012ec)
 try:call(m,0x400012e4,[],stack_top=STACK-0x7000,limit=1000000)
 finally:m.uc.hook_del(h)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0x400012ec

r={'PC_only':True,'cases':[],'failure':None,'limits':['Stock deferred enqueue, worker callback, USB decoding and primary input consumer execute.','USB completion interrupt and DMA buffer lifetime are fixtures. Interleavings are explicit, not naturally scheduled.','This tests an input-only restoration counterexample; it does not implement a complete restoration barrier.']}
try:
 for name in ['deferred_drained_while_frozen','input_only_cleanup_reopens_too_early']:
  m=make();usb_setup(m);register_release_fixture(m);m.uc.mem_write(STATE,bytes(32))
  call(m,0x40001c78,[WQ,0,0x40527f5c,128],stack_top=STACK,limit=1000)
  m.uc.mem_write(0x40526104,u32(0))
  payload=encode_usb(bytes(packets[0]))+encode_usb(changed_packet(1));m.uc.mem_write(MSG,payload)
  before=bytes(m.uc.mem_read(DATA,202))
  call(m,0x40001424,[0x4000499c,len(payload),MSG],stack_top=STACK,limit=10000)
  input_before=[int.from_bytes(m.uc.mem_read(q+4,4),'big') for q in [DQ,UQ,ALTQ]]
  assert input_before==[0,0,0] and int.from_bytes(m.uc.mem_read(WQ+4,4),'big')==1
  call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
  usb_drain(m)
  assert int.from_bytes(m.uc.mem_read(WQ+4,4),'big')==1
  if name=='input_only_cleanup_reopens_too_early':call(m,0x400ed8dc,[],stack_top=STACK,limit=1000)
  deferred_drain(m)
  assert int.from_bytes(m.uc.mem_read(UQ+4,4),'big')==2
  usb_drain(m)
  changed=bytes(m.uc.mem_read(DATA,202))!=before;phase=m.uc.mem_read(STATE,1)[0]
  assert changed==(name=='input_only_cleanup_reopens_too_early') and phase==(1 if changed else 0)
  r['cases'].append({'name':name,'MIDI_queue_counts_before':input_before,'deferred_work_pending_after_input_drain':1,'frames_published_by_deferred_callback':2,'receiver_buffer_changed':changed,'receiver_phase':phase})
  print('PASS deferred USB',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-deferred-USB-freeze-checks.json').write_text(json.dumps(r,indent=2))
