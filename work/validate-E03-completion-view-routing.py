exec(open('work/E03-receiver-test-environment.py').read())
r={'PC_only':True,'cases':[],'limits':['Notification delivered directly to view handler; kernel delivery is unexecuted.','View allocation/layout is a fixture, using the actual stock local-update provider constructor/vtable.','Stop at completion UI builder; confirmation dialog/callback lifetime is not executed.']}
try:
 m=machine()
 for p in packets:feed(m,p)
 assert sum(x['type']==18 for x in m.notes)==1
 VIEW,PROVIDER=0x47f1b000,0x47f1b200
 m.uc.mem_write(VIEW,bytes(256));call(m,0x401742d4,[PROVIDER],stack_top=STACK,limit=1000);m.uc.mem_write(VIEW+0x98,u32(PROVIDER))
 for busy in [0,1]:
  m.uc.mem_write(VIEW+0x95,bytes([busy]));m.uc.mem_write(STACK,u32(0xdeadbee0)+u32(VIEW)+u32(0x401ce141));m.uc.reg_write(UC_M68K_REG_SR,0x2700);m.uc.reg_write(UC_M68K_REG_A7,STACK)
  m.uc.emu_start(0x400c9cca,0x400c98da,count=10000);pc=m.uc.reg_read(UC_M68K_REG_PC)
  assert pc==(0x400c98da if busy==0 else 0xdeadbee0)
  r['cases'].append({'busy_flag':busy,'stop_pc':hex(pc),'completion_ui_builder_reached':pc==0x400c98da})
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'])
Path('outputs/Digitone-OS1.44E03-completion-view-routing-checks.json').write_text(json.dumps(r,indent=2));print(r)
