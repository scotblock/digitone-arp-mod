from pathlib import Path
exec(Path('work/audit-E02-startup-failure.py').read_text().split('\ntry:\n for mode')[0])
from unicorn import UC_HOOK_CODE
result={'PC_only':True,'cases':[],'limits':['Isolated native routine calls on a stock-captured allocator state; IRQ/DMA scheduling and exception unwinding do not run.','Heap exclusion is conditional on intact allocator metadata.']}
for label,source,length in [('empty_nonnull',0x47fc0000,0),('single_byte',0x47fc0000,1),('ordinary',0x47fc0000,29),('large',0x47fc0000,4096),('null_empty',0,0)]:
 m=machine();u=m.uc;main_stock=Path('work/os144/section-3.bin').read_bytes();u.mem_write(0x40000400,main_stock);m.install_isa_patches_scoped(main_stock,0x40000400)
 if source:m.ensure(source);u.mem_write(source,b'Z'*max(1,length))
 allocations=[];copies=[]
 def allocated(u,pc,n,data):
  sp=u.reg_read(UC_M68K_REG_A7);allocations.append({'header':u.reg_read(UC_M68K_REG_D0),'request':int.from_bytes(u.mem_read(sp,4),'big')})
 def copying(u,pc,n,data):
  sp=u.reg_read(UC_M68K_REG_A7)
  if int.from_bytes(u.mem_read(sp,4),'big')==0x4018ab94:copies.append(struct.unpack('>III',u.mem_read(sp+4,12)))
 u.hook_add(UC_HOOK_CODE,allocated,begin=0x401893bc,end=0x401893bc);u.hook_add(UC_HOOK_CODE,copying,begin=0x400fbad8,end=0x400fbad8)
 ret=call(m,0x4018ab1a,[source,source+length,0],stack_top=STACK,limit=2000000)
 assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 assert bytes(u.mem_read(ret,length+1))==b'Z'*length+b'\0'
 for dest,src,size in copies:
  assert dest==ret and src==source and size==length
  assert any(x['header']+12==dest and size+13<=x['request'] and 0x419f20a0<=x['header'] and x['header']+x['request']<=0x429f20a0 for x in allocations)
 if length==1:assert allocations and not copies
 if source==0:assert ret==0x419f0ea0 and not allocations and not copies
 result['cases'].append({'name':label,'bytes':length,'returned':hex(ret),'allocations':allocations,'bulk_copies':copies,'passed':True});print('PASS',label,flush=True)
result['passed']=True;Path('outputs/Digitone-E04-PC-buffer-copy-branch-controls.json').write_text(json.dumps(result,indent=2))
