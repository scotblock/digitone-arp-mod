from pathlib import Path
exec(Path('work/validate-E03-continuous-queue-action.py').read_text().split('\ntry:\n for name')[0])
r={'PC_only':True,'cases':[],'failure':None,'limits':['Actual recovered entry/exit callbacks and gate setter execute with a modeled view/provider.','Unrelated sequencer/transport stop calls are stubbed; natural page-dispatch eligibility is not established.','Broker is a host code hook, not a firmware implementation. Literal gate references do not exclude computed aliases.']}
try:
 for name in ['entry_reopens','entry_provider_disabled','exit_closes','broker_defers_entry','broker_allows_exit']:
  m=make();holder=0x47f1c000;m.uc.mem_write(holder,u32(holder+16));m.uc.mem_write(holder+16,u32(VIEW));writes=[];requests=[]
  def noop(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7);ret=int.from_bytes(uc.mem_read(sp,4),'big');uc.reg_write(UC_M68K_REG_A7,sp+4);uc.reg_write(UC_M68K_REG_PC,ret)
  for pc in [0x4009ec54,0x400967e0,0x40095310]:m.uc.hook_add(UC_HOOK_CODE,noop,begin=pc,end=pc)
  call(m,0x400ed8ea,[],stack_top=STACK,limit=1000)
  if name=='entry_provider_disabled':
   vt=0x47f1d100;m.uc.mem_write(vt,bytes(m.uc.mem_read(0x401c8f08,28)));m.uc.mem_write(vt+8,u32(0x401742e4));m.uc.mem_write(PROVIDER,u32(vt))
  def request(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7);v=int.from_bytes(uc.mem_read(sp+4,4),'big');requests.append(v)
   if name.startswith('broker') and v:uc.mem_write(sp+4,u32(0))
  m.uc.hook_add(UC_HOOK_CODE,request,begin=0x400eb524,end=0x400eb524)
  is_exit=name in ['exit_closes','broker_allows_exit']
  if is_exit:call(m,0x400ed8dc,[],stack_top=STACK,limit=1000);requests=[]
  call(m,0x400c8e6e if is_exit else 0x400c9210,[holder],stack_top=STACK,limit=100000)
  gate=int.from_bytes(m.uc.mem_read(0x419950a4,4),'big');assert gate==(1 if name=='entry_reopens' else 0)
  r['cases'].append({'name':name,'stock_gate_requests':requests,'final_gate':gate,'entry_clears_busy_flag':not is_exit and m.uc.mem_read(VIEW+0x95,1)[0]==0});print('PASS gate',name,gate,flush=True)
 r['passed']=True
except BaseException:
 import traceback;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
Path('outputs/Digitone-OS1.44E03-gate-writer-audit-checks.json').write_text(json.dumps(r,indent=2))

