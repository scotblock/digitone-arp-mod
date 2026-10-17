from pathlib import Path
source=Path('work/test-os144-stock-delayed-queue.py').read_text().split("exec(compile(s,'stock-delayed-queue','exec'))")[0]
exec(compile(source,'build-delayed-control','exec'))
s=s.replace('Digitone-OS1.44-stock-delayed-queue.json','Digitone-OS1.44-delayed-release-trace.json')
s=s.replace("if event in pending:record('queued_event_released'", """if 'delayed_queue_fixture' in r and hex(event)==r['delayed_queue_fixture']['event'] and generations[event]==r['delayed_queue_fixture']['generation']:
   sp=uc.reg_read(UC_M68K_REG_A7)
   r['target_release']={'ms':session.now_ms(),'return_address':hex(rd(uc,sp)),'stack_words':list(struct.unpack('>16I',uc.mem_read(sp,64))),'fields':list(struct.unpack('>18I',uc.mem_read(event,72))),'registers':{name:hex(uc.reg_read(reg)) for name,reg in [('D0',UC_M68K_REG_D0),('D1',UC_M68K_REG_D1),('D2',UC_M68K_REG_D2),('D3',UC_M68K_REG_D3),('D4',UC_M68K_REG_D4),('D5',UC_M68K_REG_D5),('D6',UC_M68K_REG_D6),('D7',UC_M68K_REG_D7),('A0',UC_M68K_REG_A0),('A1',UC_M68K_REG_A1),('A2',UC_M68K_REG_A2),('A3',UC_M68K_REG_A3),('A4',UC_M68K_REG_A4),('A5',UC_M68K_REG_A5),('A6',UC_M68K_REG_A6)]},**state(uc)}
  if event in pending:record('queued_event_released'""")
s=s.replace("r['fixtures'].append({'kind':'Delay one actual", """def target_write(uc,access,a,n,value,d):
    if generations[e]==r['delayed_queue_fixture']['generation']:
     r.setdefault('target_writes',[]).append({'ms':session.now_ms(),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'offset':a-e,'size':n,'value':hex(value&((1<<(8*n))-1))})
   uc.hook_add(UC_HOOK_MEM_WRITE,target_write,begin=e,end=e+71)
   r['fixtures'].append({'kind':'Delay one actual""")
exec(compile(s,'trace-stock-release','exec'))
