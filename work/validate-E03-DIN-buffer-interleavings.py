from pathlib import Path
exec(Path('work/validate-E03-receive-buffer-interleavings.py').read_text().split('\ntry:\n for name')[0])
PARSER,RING,RT,RUN,DQ=0x418f9f8c,0x429b0000,0x429f1000,0x47f40000,0x4199ff44
loop=bytes.fromhex('246f0004242f0008266f000c2f0b4280101a2f004eb9400e7eca508f538266ec4e75')
r={'PC_only':True,'cases':[],'failure':None,'limits':['UART byte arrivals and task preemption are explicitly scheduled PC fixtures.','Actual byte parser, input enqueue/wakeup, DIN consumer branch, SysEx routing and receiver run; no direct receiver invocation during interference.','Updater uses the earlier simulated flash and UI/lock/task fixtures. No hardware or new firmware.']}
try:
 for enabled in [True,False]:
  m=make();t=time.time()
  for p in packets:m.uc.mem_write(MSG,bytes(p));call(m,0x400eaac8,[MSG,len(p),8],stack_top=STACK,limit=100000);consume(m)
  for a in [PARSER,RT,RUN,0x418e9f88,0x431f2dd0,0x431f4dd0]+list(range(RING,RING+0x29000,4096)):m.ensure(a)
  m.uc.mem_write(RUN,loop);m.uc.mem_write(PARSER,u32(RING)+u32(RT)+bytes(44));m.uc.mem_write(PARSER+0x24,u32(DQ));m.uc.mem_write(PARSER+0x28,u32(0x4199fefc));m.uc.mem_write(0x418e9f88,bytes(4));m.uc.mem_write(0x4199fefc,bytes(8))
  call(m,0x40001c78,[DQ,0,0x4199fafc,256],stack_top=STACK,limit=1000)
  def stop(uc,pc,n,d):uc.emu_stop()
  h=m.uc.hook_add(UC_HOOK_CODE,stop,begin=0x401004ec,end=0x401004ec)
  m.uc.mem_write(STACK,u32(0xdeadbee0)+u32(MAN));m.uc.reg_write(UC_M68K_REG_SR,0x2000);m.uc.reg_write(UC_M68K_REG_A7,STACK);m.uc.emu_start(0x400a8690,0xdeadbee0,count=10000000);assert m.uc.reg_read(UC_M68K_REG_PC)==0x401004ec;m.uc.hook_del(h)
  ctx=m.uc.context_save();before=bytes(m.uc.mem_read(DATA,len(wire)))
  if not enabled:call(m,0x400ed8ea,[],stack_top=STACK-0x3000,limit=1000)
  for p in [bytes(packets[0]),changed_packet(1)]:
   m.uc.mem_write(MSG,p);call(m,RUN,[MSG,len(p),PARSER],stack_top=STACK-0x3000,limit=100000);assert int.from_bytes(m.uc.mem_read(DQ+4,4),'big')==1
   s=STACK-0x5000;m.uc.mem_write(s,bytes(128));m.uc.reg_write(UC_M68K_REG_A7,s);m.uc.reg_write(UC_M68K_REG_A2,0x401ce294);m.uc.reg_write(UC_M68K_REG_A3,0x40001cba);m.uc.reg_write(UC_M68K_REG_A4,0x40001d6c)
   m.uc.emu_start(0x400e9bfa,0x400e9c72,count=100000);assert m.uc.reg_read(UC_M68K_REG_PC)==0x400e9c72 and int.from_bytes(m.uc.mem_read(DQ+4,4),'big')==0
  changed=bytes(m.uc.mem_read(DATA,len(wire)))!=before;assert changed==enabled
  m.uc.context_restore(ctx);h=m.uc.hook_add(UC_HOOK_CODE,stop,begin=0x40100504,end=0x40100504);m.uc.emu_start(0x401004ec,0xdeadbee0,count=10000000);assert m.uc.reg_read(UC_M68K_REG_PC)==0x40100504;m.uc.hook_del(h)
  expected=wire[8:8+int.from_bytes(wire[:4],'big')];actual=m.flash[0x80000:0x80000+len(expected)];diff=sum(a!=b for a,b in zip(expected,actual));assert bool(diff)==enabled
  r['cases'].append({'receive_gate_enabled':enabled,'byte_parser_and_DIN_consumer_executed':True,'buffer_changed':changed,'programmed_bytes_changed':diff,'stock_executable_interval_unchanged':bytes(m.uc.mem_read(0x40000400,0x18fc00))==stock[:0x18fc00],'seconds':time.time()-t});print('PASS DIN',enabled,diff,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc()+' PC='+hex(m.uc.reg_read(UC_M68K_REG_PC));print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-DIN-buffer-interleaving-checks.json').write_text(json.dumps(r,indent=2))
