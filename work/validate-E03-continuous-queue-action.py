exec(open('work/E03-receiver-test-environment.py').read())
Q,QR,VIEW,PROVIDER,LIST,NODE,CTRL,MAN=0x4052b6bc,0x47f50000,0x47f1b000,0x47f1b200,0x47f1a000,0x47f1a100,0x47f1a200,0x47f1a300
r={'PC_only':True,'cases':[],'failure':None,'fixtures':['Registry lookup yields a modeled active update view; hardware identity, geometry and flash are simulated.','Heap allocation is bounded PC storage; strings/rendering, project save, locks/thread startup are stubbed.','Stock queue enqueue/dequeue, consumer switch, provider decisions, callback copies/destructors, work deque and worker/updater execute.']}
def make():
 m=Machine(ddr=0x08000000);m.load(stock,0x40000400);m.install_isa_patches_scoped(stock,0x40000400)
 for a in [Q,QR,VIEW,PROVIDER,LIST,NODE,CTRL,MAN,STATE,DATA,0x40400000,MSG,STACK,0x419950a4,0x419f0dc8,0x41394210,0,0x47f18000]+list(range(0x47e00000,0x47f00000,4096)):m.ensure(a)
 m.uc.mem_write(STATE,bytes(32));m.uc.mem_write(DATA,b'\xa5'*(len(wire)+512));m.heap=0x47e00000;m.freed=[];m.events=[];m.trace=[];m.actions=[];m.flash=bytearray(b'\xa6'*(4*1024*1024))
 def stub(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);ret,*args=struct.unpack('>IIIII',uc.mem_read(sp,20));result=0
  if pc==0x400e96c0:
   size=args[0];result=m.heap;m.heap+=(size+31)&~15;assert m.heap<0x47ef0000;uc.mem_write(result,bytes(size+16))
  elif pc==0x400e96cc:m.freed.append(args[0])
  elif pc in [0x4018afc8,0x4018a6be,0x4018a7a0]:uc.mem_write(args[0],bytes(4))
  elif pc==0x40016fb4:result=LIST
  elif pc==0x4014a20a:result=MAN
  elif pc==0x400fccf0:assert args[1]==5;uc.mem_write(args[0],bytes.fromhex('ef40180000'))
  elif pc==0x400fd552:result=256
  elif pc==0x400fd566:result=0x10000
  elif pc==0x400f578a:uc.mem_write(args[0],bytes(16))
  elif pc==0x400f5626:uc.mem_write(args[0],u32(0x47f18000))
  elif pc==0x400fcb2a:a=args[0];m.actions.append(('erase',a));m.flash[a:a+0x10000]=b'\xff'*0x10000
  elif pc==0x400fd402:
   a,count,src=args[:3];assert DATA+8<=src and src+count<=DATA+8+int.from_bytes(uc.mem_read(DATA,4),'big');m.actions.append(('program',a,count,src));m.flash[a:a+count]=bytes(uc.mem_read(src,count))
  uc.reg_write(UC_M68K_REG_D0,result);uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
 stubpcs=[0x400e96c0,0x400e96cc,0x4018afc8,0x4018a6be,0x4018a7a0,0x40189518,0x400c9198,0x400c92ac,0x400a0248,0x40016fb4,0x4014a20a,0x4014b4d8,0x40149f20,0x40149f46,0x40001a4c,0x400019d0,0x400017dc,0x4000170c,0x40001758,0x400018d0,0x400017ea,0x40017f24,0x4017d1ee,0x400fccf0,0x400fd552,0x400fd566,0x400f578a,0x400f5626,0x400fcb2a,0x400fd402]
 for pc in stubpcs:m.uc.hook_add(UC_HOOK_CODE,stub,begin=pc,end=pc)
 def watch(uc,pc,n,d):
  if pc==0x40001cda:
   sp=uc.reg_read(UC_M68K_REG_A7);q,msg=struct.unpack('>II',uc.mem_read(sp+4,8));m.events.append({'type':uc.mem_read(msg,1)[0],'ptr':hex(msg),'queue':hex(q)})
  else:m.trace.append(hex(pc))
 for pc in [0x40001cda,0x40001d6c,0x400c9cca,0x400c98da,0x400a87f0,0x400c93aa,0x400e61cc,0x400a8690,0x400c9536,0x40100440]:m.uc.hook_add(UC_HOOK_CODE,watch,begin=pc,end=pc)
 call(m,0x40001c78,[Q,0,QR,256],stack_top=STACK,limit=10000);call(m,0x400eb562,[Q],stack_top=STACK,limit=10000);call(m,0x400ed8dc,[],stack_top=STACK,limit=10000)
 m.uc.mem_write(VIEW,bytes(256));m.uc.mem_write(VIEW,u32(0x401c8f2c));call(m,0x401742d4,[PROVIDER],stack_top=STACK,limit=1000);m.uc.mem_write(VIEW+0x98,u32(PROVIDER));m.uc.mem_write(VIEW+0x2c,u32(LIST))
 m.uc.mem_write(LIST,bytes(64));m.uc.mem_write(LIST+0x14,u32(NODE));m.uc.mem_write(NODE,u32(LIST+0x14)+bytes(4)+u32(VIEW)+u32(CTRL));m.uc.mem_write(CTRL,bytes(4)+u32(100)+u32(100)+u32(VIEW))
 # Real work-deque constructor, with thread/lock creation explicitly stubbed.
 m.uc.mem_write(MAN,bytes(80));call(m,0x400a8950,[MAN],stack_top=STACK,limit=100000)
 m.uc.mem_write(0x402296f0,u32(0));m.uc.mem_write(0,bytes(4));m.uc.mem_write(0x47f18000,bytes(16));m.uc.mem_write(0x41395e14,b'\x01')
 return m

def consume(m, stop_callback=None):
 sp=STACK-0x200;m.uc.mem_write(sp,bytes(256));m.uc.reg_write(UC_M68K_REG_A7,sp);m.uc.reg_write(UC_M68K_REG_D3,MAN+4);m.uc.reg_write(UC_M68K_REG_D2,sp+0x7c)
 def empty(uc,pc,n,d):
  if int.from_bytes(uc.mem_read(Q+4,4),'big')==0:uc.emu_stop()
 h=m.uc.hook_add(UC_HOOK_CODE,empty,begin=0x40019cd4,end=0x40019cd4)
 stop=m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d:uc.emu_stop(),begin=stop_callback,end=stop_callback) if stop_callback else None
 try:m.uc.emu_start(0x40019ccc,0xdeadbee0,count=1000000)
 finally:
  m.uc.hook_del(h)
  if stop:m.uc.hook_del(stop)
 assert m.uc.reg_read(UC_M68K_REG_PC)==(stop_callback or 0x40019cd4)

try:
 for name in (sys.argv[1:] or ['valid','content_corrupt','missing_end','busy_view','restart_before_worker']):
  m=make();t=time.time();stream=[bytes(p) for p in packets]
  if name=='content_corrupt':
   b=bytearray(stream[100]);b[30]^=1;body=b[1:-1];seed=packets[0][8];b[-2]=(seed+sum(v^(seed+j) for j,v in enumerate(body[6:125])))&127;stream[100]=bytes(b)
  if name=='missing_end':stream=stream[:-1]
  if name=='busy_view':m.uc.mem_write(VIEW+0x95,b'\x01')
  for p in stream:
   m.uc.mem_write(MSG,bytes(p));call(m,0x400eaac8,[MSG,len(p),8],stack_top=STACK,limit=100000);consume(m)
  if name!='content_corrupt':assert bytes(m.uc.mem_read(DATA,len(wire)))==wire
  if name=='restart_before_worker':
   m.uc.mem_write(MSG,bytes(packets[0]));call(m,0x400eaac8,[MSG,len(packets[0]),8],stack_top=STACK,limit=100000);consume(m)
   assert call(m,0x400eab94,[],stack_top=STACK,limit=10000)==0
  entry=int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big');end=int.from_bytes(m.uc.mem_read(MAN+0x3c,4),'big')
  case={'name':name,'queued_work_items':(end-entry)//36,'completed_phase':m.uc.mem_read(STATE,1)[0]}
  if name in ['missing_end','busy_view']:
   assert entry==end and not m.actions and '0x400c9536' not in m.trace;case.update(no_work_callback=True,no_flash_calls=True)
  else:
   assert end-entry==36
   retained=bytes(m.uc.mem_read(entry,36));context=int.from_bytes(retained[:4],'big');assert int.from_bytes(m.uc.mem_read(context,4),'big')==VIEW and context not in m.freed
   # Destroy old caller frames before actual worker entry; callback must use its retained heap context.
   m.uc.mem_write(STACK-0x1800,b'\xa7'*0x2000)
   idle=[0]
   def boundary(uc,pc,n,d):
    if pc==0x40100504:uc.emu_stop()
    elif pc==0x400a86bc:
     idle[0]+=1
     if idle[0]>1:uc.emu_stop()
   hooks=[m.uc.hook_add(UC_HOOK_CODE,boundary,begin=x,end=x) for x in [0x40100504,0x400a86bc]]
   call(m,0x400a8690,[MAN],stack_top=STACK-0x800,limit=10000000)
   for h in hooks:m.uc.hook_del(h)
   pc=m.uc.reg_read(UC_M68K_REG_PC);case.update(worker_stop_pc=hex(pc),retained_context=hex(context),temporary_frames_overwritten=True,work_record=retained.hex())
   if name=='valid':
    assert pc==0x40100504
    expected=wire[8:8+int.from_bytes(wire[:4],'big')];assert m.flash[0x80000:0x80000+len(expected)]==expected
    assert m.flash[0x380000:0x380200]==b'\xa6'*512
    case.update(exact_received_image_programmed=True,stock_data_guard_intact=True)
   else:
    assert pc==0x400a86bc and not m.actions
    assert int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big')==end
    case.update(no_flash_calls=True,work_queue_drained=True,context_released=context in m.freed)
    assert int.from_bytes(m.uc.mem_read(Q+4,4),'big')==1
    m.uc.mem_write(STACK-0x1800,b'\xa7'*0x2000);consume(m,stop_callback=0x400c9c6a)
    case.update(error_callback_reached_by_stock_consumer=True,temporary_worker_frames_overwritten=True)
  assert bytes(m.uc.mem_read(0x40000400,0x18fc00))==stock[:0x18fc00];case['executable_interval_40000400_to_40190000_unchanged']=True
  case.update(program_calls=sum(x[0]=='program' for x in m.actions),erase_calls=sum(x[0]=='erase' for x in m.actions),event_counts={str(k):sum(x['type']==k for x in m.events) for k in [6,18,19,20]},seconds=time.time()-t,trace_counts={k:m.trace.count(k) for k in sorted(set(m.trace))})
  r['cases'].append(case);print('PASS',name,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+(' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC)) if 'm' in globals() else '');print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-continuous-queue-action-checks.json').write_text(json.dumps(r,indent=2))





