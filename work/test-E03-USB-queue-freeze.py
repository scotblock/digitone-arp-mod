from pathlib import Path
exec(Path('work/test-E03-receive-freeze-design.py').read_text().split('\ntry:\n for name')[0])
UQ,ALTQ=0x4199ff24,0x4199ff04

def usb_setup(m):
 for a in [0x418e9f6c,0x418f9f8c,0x431f2948,0x431f4dd4,0x429f218c,0x4199fefc]:m.ensure(a)
 call(m,0x400e819c,[],stack_top=STACK,limit=100000)
 for q,ring in [(DQ,0x4199fafc),(UQ,0x4199f6fc),(ALTQ,0x4199f2fc)]:call(m,0x40001c78,[q,0,ring,256],stack_top=STACK,limit=1000)
 for slot,q in [(0,DQ),(1,UQ),(2,ALTQ)]:call(m,0x400e83f0,[slot,q,0x4199fefc],stack_top=STACK,limit=1000)
 def no_wait(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 m.uc.hook_add(UC_HOOK_CODE,no_wait,begin=0x4000185e,end=0x4000185e)
 call(m,0x400047e2,[0x400e8440,0x400e8674],stack_top=STACK,limit=1000)

def usb_feed(m,p,alternate=False):
 m.uc.mem_write(MSG,bytes(p));call(m,0x400e8674 if alternate else 0x400e8440,[MSG,len(p)],stack_top=STACK-0x3000,limit=100000)

def usb_drain(m):
 def idle(uc,pc,n,d):
  if all(int.from_bytes(uc.mem_read(q+4,4),'big')==0 for q in [DQ,UQ,ALTQ]):uc.emu_stop()
 h=m.uc.hook_add(UC_HOOK_CODE,idle,begin=0x400e9bea,end=0x400e9bea)
 try:call(m,0x400e9b7e,[],stack_top=STACK-0x5000,limit=1000000)
 finally:m.uc.hook_del(h)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0x400e9bea
r={'PC_only':True,'cases':[],'failure':None}
try:
 for alternate in [False,True]:
  for freeze in [False,True]:
   m=make();usb_setup(m);m.uc.mem_write(STATE,bytes(32));before=bytes(m.uc.mem_read(DATA,202))
   for p in [bytes(packets[0]),changed_packet(1)]:usb_feed(m,p,alternate)
   counts=[int.from_bytes(m.uc.mem_read(q+4,4),'big') for q in [DQ,UQ,ALTQ]];assert sum(counts)==2
   if freeze:call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
   usb_drain(m)
   phase=m.uc.mem_read(STATE,1)[0];changed=bytes(m.uc.mem_read(DATA,202))!=before
   pending=int.from_bytes(m.uc.mem_read(STACK-0x5000-48+44,4),'big')
   if not alternate:assert changed==(not freeze) and phase==(0 if freeze else 1)
   else:assert not changed and phase==0
   r['cases'].append({'alternate_USB_callback':alternate,'gate_frozen':freeze,'queued_counts':counts,'receive_buffer_changed':changed,'phase':phase,'secondary_route_not_certified':alternate,'pending_stack_word':hex(pending),'queue_counts_after':[int.from_bytes(m.uc.mem_read(q+4,4),'big') for q in [DQ,UQ,ALTQ]]});print('PASS USB',alternate,freeze,flush=True)
 r['passed']=True
 r['limits']=['Primary USB bulk callback and input task execute from registered software callback boundary; endpoint hardware/pacing are fixtures.','Secondary callback queues drain but do not reach receiver in this run; its pending-message/consumer path remains unresolved.','Queue-count zero is not used as a sufficient restoration certificate.']
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-USB-queue-freeze-checks.json').write_text(json.dumps(r,indent=2))

