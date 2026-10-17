from pathlib import Path
exec(Path('work/test-PC-persistent-admission.py').read_text().split('\nout=')[0])
from capstone import Cs,CS_ARCH_M68K,CS_MODE_M68K_040
audit_stock=Path('work/os144/section-3.bin').read_bytes();audit_image=Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes();base=0x40000400
cs=Cs(CS_ARCH_M68K,CS_MODE_M68K_040)
out={'PC_only':True,'static_ranges':{},'references':{},'native_consumption_controls':[]}
for lo,hi in [(0x4000045c,0x400004e8),(0x400004e8,0x40000570),(0x4029c4b0,0x4029c51e),(0x4008d2fa,0x4008d33c),(0x4009c5a0,0x4009c652),(0x4009d0d8,0x4009d0f4)]:
 out['static_ranges'][hex(lo)]=[{'pc':hex(i.address),'bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operand':i.op_str} for i in cs.disasm(audit_image[lo-base:hi-base],lo)]
for target in [0x400004e8,0x40000538,0x4029c4b0,0x4029c518,0x40001df4,0x4009c5a0]:
 hits=[];start=0;needle=u32(target)
 while (start:=audit_image.find(needle,start))>=0:hits.append(hex(base+start));start+=1
 relative=[]
 for off in range(0,len(audit_stock)-6,2):
  w=int.from_bytes(audit_stock[off:off+2],'big');pc=base+off;dest=None
  if w>>8==0x61:
   d=w&255
   if d==0:dest=pc+2+int.from_bytes(audit_stock[off+2:off+4],'big',signed=True)
   elif d!=255:dest=pc+2+(d if d<128 else d-256)
  elif w==0x4eba:dest=pc+2+int.from_bytes(audit_stock[off+2:off+4],'big',signed=True)
  if dest==target:relative.append(hex(pc))
 out['references'][hex(target)]={'literal_candidates':hits,'aligned_relative_call_candidates':relative,'computed_call_exclusion':False}
# Seed remains a declared PC fixture. Consumption is actual native code and
# occurs after the actual copier, before the stock wrapper mutates note pools.
for failure in ['none','bad_metadata','unready']:
 m=prepared();install(m,PHASE['live']);u=m.uc
 u.reg_write(UC_M68K_REG_SR,0x2710);u.reg_write(UC_M68K_REG_A7,RESETSTACK);u.emu_start(0x4029c4b0,0x40001df4,count=100000)
 assert u.reg_read(UC_M68K_REG_PC)==0x40001df4 and rd(u,ADDR)==0
 u.mem_write(ADDR,u32(PHASE['cold']))
 assert native(m,'claim_cold',sr=0x251f)==1 and rd(u,ADDR)==PHASE['initializing']
 if failure=='bad_metadata':u.mem_write(0x47be1004,u32(0))
 if failure=='unready':u.mem_write(0x47be1010,u32(0))
 actual=[]
 def init(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7)
  actual.append({'return':hex(rd(u,sp)),'argument':rd(u,sp+4),'admission':hex(rd(u,ADDR))})
  assert rd(u,ADDR)==PHASE['initializing'] and rd(u,sp)==0x4009c5aa and rd(u,sp+4)==158,actual
 h=u.hook_add(UC_HOOK_CODE,init,begin=0x400ffed0,end=0x400ffed0)
 call(m,0x4009c5a0,[],stack_top=RESETSTACK,limit=400000);u.hook_del(h)
 assert len(actual)==1 and native(m,'claim_cold')==0 and rd(u,ADDR)==PHASE['initializing']
 out['native_consumption_controls'].append({'failure':failure,'actual_wrapper_and_stock_initializer':actual,'cold_seed_host_fixture':True,'claim_native':True,'replay_claim_denied':True,'outer_setup_completion_not_run':True})
out['passed']=True
out['normal_diagnostic_branch_controls']=[]
for flags in [0x00140000,0x00140040]:
 m=prepared();u=m.uc;u.mem_write(0x402296f0,u32(flags));u.reg_write(UC_M68K_REG_SR,0x201f)
 target=0x4008d326 if flags&0x40 else 0x4008d312
 u.emu_start(0x4008d308,target,count=100)
 assert u.reg_read(UC_M68K_REG_PC)==target and u.reg_read(UC_M68K_REG_D0)==flags&0x40
 out['normal_diagnostic_branch_controls'].append({'flags':hex(flags),'selected':hex(target),'stock_mask_branch_executed':True,'setup_calls_not_run':True})
out['limits']=['This audit does not add bootstrap/initializer admission hooks.','Cold seed is fixture supplied; native stock wrapper and helper run as separate controlled calls.','Raw/relative references cannot exclude computed warm entry or forged call provenance.','Actual complete setup failure/normal-mode contract, physical storage/cache/timing remain unproven.']
Path('outputs/Digitone-E04-PC-cold-permit-boundary-audit.json').write_text(json.dumps(out,indent=2))
print('PASS three native post-copy consumption / real initializer controls')
print(json.dumps(out['references'],indent=2))
