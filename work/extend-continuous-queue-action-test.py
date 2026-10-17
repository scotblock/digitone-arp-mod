from pathlib import Path
p=Path('work/validate-E03-continuous-queue-action.py').read_text()
p=p.replace("['valid']", "['valid','content_corrupt','missing_end','busy_view']")
p=p.replace("m=make();t=time.time()\n  for p in packets:","m=make();t=time.time();stream=[bytes(p) for p in packets]\n  if name=='content_corrupt':\n   b=bytearray(stream[100]);b[30]^=1;body=b[1:-1];seed=packets[0][8];b[-2]=(seed+sum(v^(seed+j) for j,v in enumerate(body[6:125])))&127;stream[100]=bytes(b)\n  if name=='missing_end':stream=stream[:-1]\n  if name=='busy_view':m.uc.mem_write(VIEW+0x95,b'\\x01')\n  for p in stream:")
a=p.index('  assert bytes(m.uc.mem_read(DATA,len(wire)))==wire')
b=p.index("  r['cases'].append",a)
p=p[:a]+'''  if name!='content_corrupt':assert bytes(m.uc.mem_read(DATA,len(wire)))==wire
  entry=int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big');end=int.from_bytes(m.uc.mem_read(MAN+0x3c,4),'big')
  case={'name':name,'queued_work_items':(end-entry)//36,'completed_phase':m.uc.mem_read(STATE,1)[0]}
  if name in ['missing_end','busy_view']:
   assert entry==end and not m.actions and '0x400c9536' not in m.trace;case.update(no_work_callback=True,no_flash_calls=True)
  else:
   assert end-entry==36
   retained=bytes(m.uc.mem_read(entry,36));context=int.from_bytes(retained[:4],'big');assert int.from_bytes(m.uc.mem_read(context,4),'big')==VIEW and context not in m.freed
   # Destroy old caller frames before actual worker entry; callback must use its retained heap context.
   m.uc.mem_write(STACK-0x1800,b'\\xa7'*0x2000)
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
    assert m.flash[0x380000:0x380200]==b'\\xa6'*512
    case.update(exact_received_image_programmed=True,stock_data_guard_intact=True)
   else:
    assert pc==0x400a86bc and not m.actions
    assert int.from_bytes(m.uc.mem_read(MAN+0x2c,4),'big')==end
    case.update(no_flash_calls=True,work_queue_drained=True,context_released=context in m.freed)
''' +p[b:]
a=p.index("  r['cases'].append")
b=p.index(" r['passed']=True",a)
p=p[:a]+'''  case.update(program_calls=sum(x[0]=='program' for x in m.actions),erase_calls=sum(x[0]=='erase' for x in m.actions),event_counts={str(k):sum(x['type']==k for x in m.events) for k in [6,18,19,20]},seconds=time.time()-t,trace_counts={k:m.trace.count(k) for k in sorted(set(m.trace))})
  r['cases'].append(case);print('PASS',name,flush=True)
'''+p[b:]
Path('work/validate-E03-continuous-queue-action.py').write_text(p)
