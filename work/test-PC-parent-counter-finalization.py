from pathlib import Path
exec(Path('work/test-PC-resident-storage-extended-runtime.py').read_text().split('\ntry:')[0])
from emu.harness import call
from unicorn import UC_HOOK_CODE
out={'PC_only':True,'cases':[],'limits':['Calls are stopped-state native fixtures. Counter=1 is explicitly supplied and does not establish natural shutdown reachability or scheduling exclusion. No IRQ/DMA timing is modeled during these calls.']}
for mode in ['balanced_initializer_finalizer','nonlast_finalizer','forced_last_finalizer']:
 row={'mode':mode,'releases':[],'frees':[]};out['cases'].append(row);s=None
 try:
  s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000);m=s.m;u=m.uc;stack=0x47fdff00;m.ensure(stack)
  def state():
   ctrl=rd(u,0x419f0de4)
   return {'counter':(rd(u,0x419f0d70)<<32)|rd(u,0x419f0d74),'strong':rd(u,ctrl+4),'owner_vtable':hex(rd(u,0x41a720d0))}
  def released(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7)
   if rd(u,sp+4)==0x419f0de4:row['releases'].append({'caller':hex(rd(u,sp))})
  def freed(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7)
   if rd(u,sp+4)==0x41a720a0:row['frees'].append(hex(rd(u,sp+4)))
  u.hook_add(UC_HOOK_CODE,released,begin=0x40146456,end=0x40146456);u.hook_add(UC_HOOK_CODE,freed,begin=0x400e96cc,end=0x400e96cc)
  row['before']=state();assert row['before']['counter']==94
  if mode=='balanced_initializer_finalizer':
   call(m,0x4014d9e4,[],stack_top=stack,limit=50000);row['after_initializer']=state();assert row['after_initializer']['counter']==95
  elif mode=='forced_last_finalizer':u.mem_write(0x419f0d70,struct.pack('>II',0,1));row['fixture']=state()
  call(m,0x4001c92a,[],stack_top=stack,limit=3000000);row['after']=state();row['returned']=u.reg_read(UC_M68K_REG_PC)==0xdeadbee0;assert row['returned']
  if mode=='forced_last_finalizer':assert row['after']['counter']==0 and row['releases'] and row['frees'] and row['after']['owner_vtable']=='0x40195abc'
  else:assert row['after']['counter']==(94 if mode=='balanced_initializer_finalizer' else 93) and not row['releases'] and not row['frees'] and row['after']['owner_vtable']==row['before']['owner_vtable']
  row['passed']=True
 except Exception:row.update(passed=False,failure=traceback.format_exc());print(row['failure'],flush=True)
 finally:
  if s:s.close()
 print(mode,row.get('passed'),flush=True)
out['passed']=all(r.get('passed') for r in out['cases']);Path('outputs/Digitone-E04-PC-parent-counter-finalization.json').write_text(json.dumps(out,indent=2))
if not out['passed']:raise SystemExit(1)
