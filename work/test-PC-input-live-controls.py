from pathlib import Path
exec(Path('work/probe-PC-startup-note-admission.py').read_text().split('\nout=')[0])
import hashlib
from unicorn import UC_HOOK_MEM_WRITE
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
input_cfg=json.loads(Path('work/os144/PC_ONLY-input-live-overlay.json').read_text());input_blob=Path('work/os144/PC_ONLY-input-live-overlay.bin').read_bytes()
phase_cfg=json.loads(Path('work/os144/PC_ONLY-persistent-admission.json').read_text());P=phase_cfg['phases'];STATE=input_cfg['state']
position=0
while position<len(input_blob):
 ins=cfisa.decode(lambda off:int.from_bytes(input_blob[position+off:position+off+2],'big'),input_cfg['base']+position)
 assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(input_blob[position:position+2],'big')),(hex(input_cfg['base']+position),ins.op)
 position+=ins.length
assert position==len(input_blob)
def install_inputs(m):
 m.load(input_blob,input_cfg['base']);m.install_isa_patches_scoped(input_blob,input_cfg['base'])
 for hook in input_cfg['hooks']:
  assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']
  m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))
def fingerprint(u):
 return hashlib.sha256(bytes(u.mem_read(0x419eb92c,0x4000))+bytes(u.mem_read(0x47be1000,0xb74))+bytes(u.mem_read(0x47be2000,2080))+bytes(u.mem_read(0x41368d20,0x70))+bytes(u.mem_read(0x400002fc,4))).hexdigest()
def invoke(u,entry,args,ret=0xdeadbee0,sr=0x201f,count=300000):
 stack=0x47fdff00;u.mem_write(stack,u32(ret)+b''.join(u32(v) for v in args));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,stack);u.emu_start(entry,ret,count=count)
def regs(u):return [u.reg_read(r) for r in list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+7))]
out={'PC_only':True,'ISA_C_MOVE_audit_passed':True,'denial_cases':[],'stock_parity':[],'completion_cases':[]}
pre=Path('work/startup-producer-order-E04_restored/producer-0x4009d0d8.snap')
m=restored(pre);install_inputs(m);u=m.uc
for phase in [P['cold'],P['initializing'],P['failed'],0,0xa5a5a5a5,P['live']^1]:
 for hook in input_cfg['hooks'][:3]:
  u.mem_write(STATE,u32(phase));before=fingerprint(u);saved=regs(u);invoke(u,hook['site'],[0]*8)
  assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and u.reg_read(UC_M68K_REG_A7)==0x47fdff04 and u.reg_read(UC_M68K_REG_SR)==0x201f
  assert regs(u)==saved and fingerprint(u)==before
  out['denial_cases'].append({'phase':hex(phase),'entry':hook['name'],'null_arguments_not_dereferenced':True,'context_pool_queue_config_vector_unchanged':True,'full_register_SR_and_stack_preservation':True})
# Paired LIVE calls on identical saved stock state; no timers/peripheral input.
for point in [0x4008d31e,0x4008d3ec]:
 for ready in [1,0]:
  result=[]
  for guarded in [False,True]:
   m=restored(Path('work/startup-producer-order-E04_restored')/('producer-'+hex(point)+'.snap'));u=m.uc
   if guarded:install_inputs(m)
   u.mem_write(STATE,u32(P['live']))
   if not ready:u.mem_write(0x47be1000,u32(0));u.mem_write(0x47be1010,u32(0))
   packet=0x47fc6000;m.ensure(packet);m.ensure(0x47fdff00);channel=rd(u,0x41368d2c)&15;u.mem_write(packet,bytes([0x90|channel,64,100]));hits=[]
   for pc in [0x400eb166,0x400eae5c,0x400eaf48,0x40100252]:u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:hits.append(hex(pc)),begin=pc,end=pc)
   invoke(u,0x400eb2d2,[packet,3,8]);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   result.append({'hash':fingerprint(u),'regs':regs(u),'SR':u.reg_read(UC_M68K_REG_SR),'SP':u.reg_read(UC_M68K_REG_A7),'hits':hits})
  assert result[0]==result[1],(point,ready,result)
  assert '0x40100252' in result[1]['hits'] and '0x400eaf48' in result[1]['hits']
  out['stock_parity'].append({'point':hex(point),'optional_feature_enabled':bool(ready),'native_state_CPU_and_route_parity':True,'cached_publications_before_live_producer':point==0x4008d31e})
# Exact post-return checkpoint controls. The original final stock call already
# executed in this snapshot; start at completion+6 rather than execute it twice.
for kind in ['normal','disabled_feature','bad_magic','unready','bad_state','test_mode','bad_flags','bad_audio_vector','wrong_return']:
 m=restored('work/startup-producer-order-E04_restored/producer-0x4008d3ec.snap');install_inputs(m);u=m.uc;m.ensure(0x47fdff00)
 if kind=='disabled_feature':u.mem_write(0x47be1000,u32(0));u.mem_write(0x47be1010,u32(0))
 if kind=='bad_magic':u.mem_write(0x47be1004,u32(0))
 if kind=='unready':u.mem_write(0x47be1010,u32(0))
 if kind=='bad_state':u.mem_write(STATE,u32(P['live']))
 if kind=='test_mode':u.mem_write(0x402a0e50,u32(1))
 if kind=='bad_flags':u.mem_write(0x40236788,u32(0))
 if kind=='bad_audio_vector':u.mem_write(0x400002fc,u32(0))
 saved=regs(u);stores=[]
 def statewrite(u,access,a,n,v,d):
  if a<STATE+4 and a+n>STATE:stores.append({'value':v,'IPL':(u.reg_read(UC_M68K_REG_SR)>>8)&7})
 u.hook_add(UC_HOOK_MEM_WRITE,statewrite)
 ret=0xdeadbee0 if kind=='wrong_return' else 0x4008d3fa
 invoke(u,input_cfg['layout']['normal_completion']['address']+6,[],ret=ret,count=2000)
 valid=kind in ['normal','disabled_feature','bad_magic','unready']
 assert rd(u,STATE)==P['live' if valid else 'failed'] and len(stores)==1 and stores[0]['IPL']==7
 if valid:
  assert u.reg_read(UC_M68K_REG_PC)==ret and u.reg_read(UC_M68K_REG_SR)==0x201f and regs(u)==saved and u.reg_read(UC_M68K_REG_A7)==0x47fdff04
  assert rd(u,0x47be1000)==(0x47bccf04 if kind=='normal' else 0)
 else:assert u.reg_read(UC_M68K_REG_PC)!=ret and u.reg_read(UC_M68K_REG_SR)&0xff00==0x2700
 out['completion_cases'].append({'kind':kind,'LIVE':valid,'state_store_IPL7':True,'stock_final_call_already_returned_checkpoint':True,'optional_stock_fallback':valid and kind!='normal'})
out['passed']=True
out['limits']=input_cfg['limits']+['Completion controls use an actual post-stock-return checkpoint; continuous startup is validated separately.','LIVE pass-through parity uses no concurrent timers/IRQ execution; physical timing is unverified.']
Path('outputs/Digitone-E04-PC-input-live-controls.json').write_text(json.dumps(out,indent=2))
print('PASS',len(out['denial_cases']),'input denials,',len(out['stock_parity']),'LIVE parity pairs,',len(out['completion_cases']),'completion controls')
