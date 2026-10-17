from pathlib import Path
exec(Path('work/test-PC-resident-storage-extended-runtime.py').read_text().split('\ntry:')[0])
from emu.harness import call
from unicorn import UC_HOOK_CODE
out={'PC_only':True,'cases':[],'limits':['Parent/child destruction is forced on a stopped restored state while a deliberately retained raw descriptor exists; no real application admission/scheduling preconditions are established.','Native routine execution is bounded; failed continuation is not automatically a physical-device bug.']}
for mode,entry,target in [('child_teardown',0x4015141c,0x41a720d0),('parent_teardown',0x40152a1c,0x41a720a0),('parent_delete',0x40152bae,0x41a720a0)]:
 row={'mode':mode,'entry':hex(entry),'native_frees':[],'conversions':[],'failure':None};out['cases'].append(row);s=None
 try:
  s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000);m=s.m;u=m.uc;stack=0x47fdff00;slot=0x47fc0100;m.ensure(stack);m.ensure(slot);backing_before=hashlib.sha256(bytes(u.mem_read(0x407ef9f4,0x3000))).hexdigest();queue_before=bytes(u.mem_read(LO,spec['storage_bytes']))
  descriptor=call(m,0x400e96c0,[8],stack_top=stack,limit=2000000);assert descriptor;u.mem_write(descriptor,struct.pack('>II',0x41a720d0,0x407ef9f4));u.mem_write(slot,struct.pack('>I',descriptor))
  def freed(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);row['native_frees'].append({'pointer':hex(rd(u,sp+4)),'caller':hex(rd(u,sp))})
  def convert(u,pc,n,d):
   sp=u.reg_read(UC_M68K_REG_A7);row['conversions'].append({'destination':hex(rd(u,sp+4)),'source':hex(rd(u,sp+8))})
  u.hook_add(UC_HOOK_CODE,freed,begin=0x400e96cc,end=0x400e96cc);u.hook_add(UC_HOOK_CODE,convert,begin=0x4000a1a6,end=0x4000a1a6)
  call(m,entry,[target],stack_top=stack,limit=3000000);row['destructor_returned']=u.reg_read(UC_M68K_REG_PC)==0xdeadbee0;row['destructor_end_pc']=hex(u.reg_read(UC_M68K_REG_PC));row['owner_vtable_after']=hex(rd(u,0x41a720d0));row['parent_vtable_after']=hex(rd(u,0x41a720a0));row['backing_unchanged_by_teardown']=hashlib.sha256(bytes(u.mem_read(0x407ef9f4,0x3000))).hexdigest()==backing_before;row['retained_descriptor_after']=bytes(u.mem_read(descriptor,8)).hex();row['parent_freed']=any(x['pointer']=='0x41a720a0' for x in row['native_frees'])
  if row['destructor_returned']:
   vtable=rd(u,0x41a720d0);row['getter_after']=hex(rd(u,vtable+0x28));call(m,0x4002c1d2,[slot],stack_top=stack,limit=300000);row['callback_returned']=u.reg_read(UC_M68K_REG_PC)==0xdeadbee0;row['callback_end_pc']=hex(u.reg_read(UC_M68K_REG_PC));row['halt_vector']=m.halt_vec
  row['queue_unchanged']=bytes(u.mem_read(LO,spec['storage_bytes']))==queue_before;row['completed']=True
 except Exception:row.update(completed=False,failure=traceback.format_exc(),end_pc=hex(s.m.uc.reg_read(UC_M68K_REG_PC)) if s else None);print(row['failure'],flush=True)
 finally:
  if s:s.close()
 print('DESTRUCTION',mode,row.get('destructor_returned'),row.get('callback_returned'),row.get('completed'),flush=True)
Path('outputs/Digitone-E04-PC-parent-destruction-retained-callback.json').write_text(json.dumps(out,indent=2))
