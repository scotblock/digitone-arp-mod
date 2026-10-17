from pathlib import Path
import json
s=Path('work/test-PC-deferred-release-startup.py').read_text()
s=s.replace('PC_ONLY-deferred-release-overlay','PC_ONLY-resident-deferred-release-overlay').replace('deferred-release-startup-','resident-deferred-startup-')
s=s.replace("m.ensure(native_defer_spec['count']);m.uc.mem_write(native_defer_spec['count'],bytes(native_defer_spec['storage_bytes']))", "m.ensure(native_defer_spec['count']);m.uc.mem_write(native_defer_spec['count'],bytes([0xa5])*native_defer_spec['storage_bytes'])")
anchor="  for deferred_hook in [h for h in native_defer_spec['hooks'] if h['name']!='completion_dispatch']:"
add="""  row['deferred_storage_writes']={};row['deferred_initialization_checks']=[]
  def storage_write(u,access,address,length,value,data):
   if not (0x40000000<=address<0x80000000):return
   canonical=0x40000000+(address-0x40000000)%0x08000000
   if canonical<native_defer_spec['count']+native_defer_spec['storage_bytes'] and canonical+length>native_defer_spec['count']:
    pc=hex(u.reg_read(UC_M68K_REG_PC));record=row['deferred_storage_writes'].setdefault(pc,{'writes':0,'min':hex(canonical),'max':hex(canonical+length)})
    record['writes']+=1;record['min']=hex(min(int(record['min'],16),canonical));record['max']=hex(max(int(record['max'],16),canonical+length))
  for alias in range(8):
   start=native_defer_spec['count']+alias*0x08000000;m.uc.hook_add(UC_HOOK_MEM_WRITE,storage_write,begin=start-64,end=start+native_defer_spec['storage_bytes']+63)
  def initialized_before_seed(u,pc,n,data):
   actual=bytes(u.mem_read(native_defer_spec['count'],native_defer_spec['storage_bytes']));assert actual==bytes(native_defer_spec['storage_bytes'])
   row['deferred_initialization_checks'].append({'pc':hex(pc),'queue_all_zero':True,'phase_before_seed':int.from_bytes(u.mem_read(0x47be2840,4),'big')})
  m.uc.hook_add(UC_HOOK_CODE,initialized_before_seed,begin=0x4029c518,end=0x4029c518)
"""
assert anchor in s;s=s.replace(anchor,add+anchor)
s=s.replace("r['deferred_queue_zero_initialized_by_host_fixture']=True;r['additional_storage_host_cleared']=True;", "r['deferred_queue_zero_initialized_by_host_fixture']=False;r['additional_storage_host_cleared']=False;r['deferred_queue_initially_dirtied_by_host']=True;")
s=s.replace('New deferred-release queue is host-zeroed at installation; no owned/packaged native cold initialization is established.','Queue was deliberately dirty at installation and zeroed by native payload copying before COLD seeding. Code delivery and physical/global ownership remain unverified.')
exec(compile(s,'resident-deferred-startup','exec'))
