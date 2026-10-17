from pathlib import Path
exec(Path('work/test-PC-persistent-admission.py').read_text().split('\nout=')[0])
boot_guard_cfg=json.loads(Path('work/os144/PC_ONLY-cold-admission-overlay.json').read_text())
boot_guard_blob=Path('work/os144/PC_ONLY-cold-admission-overlay.bin').read_bytes()
from unicorn import UC_HOOK_MEM_WRITE
pos=0
while pos<len(boot_guard_blob):
 ins=cfisa.decode(lambda off:int.from_bytes(boot_guard_blob[pos+off:pos+off+2],'big'),boot_guard_cfg['base']+pos)
 assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(boot_guard_blob[pos:pos+2],'big')),(hex(boot_guard_cfg['base']+pos),ins.op)
 pos+=ins.length
assert pos==len(boot_guard_blob)
def setup_boot_guard(m):
 install(m,0);m.load(boot_guard_blob,boot_guard_cfg['base']);m.install_isa_patches_scoped(boot_guard_blob,boot_guard_cfg['base'])
def execute_seed(m,state,ret=0x4000053e,sr=0x251f):
 u=m.uc;u.mem_write(ADDR,u32(state));u.mem_write(0x47fdff00,u32(ret));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,0x47fdff00)
 u.emu_start(boot_guard_cfg['layout']['seed_after_copy']['address'],0x40001df4,count=300)
 return u.reg_read(UC_M68K_REG_PC)
out={'PC_only':True,'ISA_C_MOVE_audit_passed':True,'seed_cases':[],'refusal_cases':[]}
for kind in ['valid','live','failed','unknown','wrong_return','bad_header']:
 m=prepared();setup_boot_guard(m);u=m.uc
 state={'live':PHASE['live'],'failed':PHASE['failed'],'unknown':0xa5a5a5a5}.get(kind,0)
 if kind=='bad_header':u.mem_write(0x47be1004,u32(0))
 before={r:u.reg_read(r) for r in REGS if r not in [UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_SR]}
 pc=execute_seed(m,state,0xdeadbee0 if kind=='wrong_return' else 0x4000053e)
 if kind=='valid':
  assert pc==0x40001df4 and rd(u,ADDR)==PHASE['cold'] and u.reg_read(UC_M68K_REG_SR)==0x251f and u.reg_read(UC_M68K_REG_A7)==0x47fdff00
  assert all(u.reg_read(r)==v for r,v in before.items())
 else:assert rd(u,ADDR)==PHASE['failed'] and u.reg_read(UC_M68K_REG_SR)&0xff00==0x2700 and rd(u,0x47be1010)==0 and rd(u,0x47be1000)==0
 out['seed_cases'].append({'kind':kind,'seeded':kind=='valid','denial_stops_no_return':kind!='valid'})
for kind in ['live','zero','unknown','diagnostic','wrong_return']:
 m=prepared();setup_boot_guard(m);u=m.uc
 state={'live':PHASE['live'],'zero':0,'unknown':0xa5a5a5a5}.get(kind,PHASE['cold']);u.mem_write(ADDR,u32(state))
 u.mem_write(0x402296f0,u32(0x00140040 if kind=='diagnostic' else 0x00140000));before=state_of(m);flags=bytes(u.mem_read(0x40236788,4))+bytes(u.mem_read(0x41392fa4,4));hits=[];stores=[]
 metadata_before=bytearray(u.mem_read(0x47be1000,0xb74));sidecar_before=bytes(u.mem_read(0x47be2000,2080))
 for p in [0x4009d0d8,0x400ffed0,0x4008b05c,0x4008e8b2]:u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:hits.append(hex(pc)),begin=p,end=p)
 def watched(u,access,a,n,v,d):
  if a<ADDR+4 and a+n>ADDR:stores.append({'pc':hex(u.reg_read(UC_M68K_REG_PC)),'IPL':(u.reg_read(UC_M68K_REG_SR)>>8)&7})
 u.hook_add(UC_HOOK_MEM_WRITE,watched)
 u.mem_write(0x47fdff00,u32(0xdeadbee0 if kind=='wrong_return' else 0x4008d31e));u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.reg_write(UC_M68K_REG_SR,0x201f)
 u.emu_start(boot_guard_cfg['layout']['normal_setup_claim']['address'],0xdeadbee0,count=500)
 after=state_of(m)
 assert not hits and all(after[k]==v for k,v in before.items() if k!='context_hash') and flags==bytes(u.mem_read(0x40236788,4))+bytes(u.mem_read(0x41392fa4,4)),(kind,hits,before,after)
 metadata_before[:4]=bytes(4);metadata_before[16:20]=bytes(4)
 assert bytes(u.mem_read(0x47be1000,0xb74))==bytes(metadata_before) and bytes(u.mem_read(0x47be2000,2080))==sidecar_before
 assert rd(u,ADDR)==PHASE['failed'] and u.reg_read(UC_M68K_REG_SR)&0xff00==0x2700 and len(stores)==1 and stores[0]['IPL']==7
 assert u.reg_read(UC_M68K_REG_PC)!=0xdeadbee0
 out['refusal_cases'].append({'kind':kind,'setup_flags_note_queue_context_slots_and_audio_vector_preserved':True,'context_PTR_and_READY_explicitly_disabled':True,'setup_initializer_diagnostic_not_called':True,'failure_state_store_under_IPL7':True,'proposed_cold_stop_not_stock_recovery':True})
out['passed']=True;out['limits']=boot_guard_cfg['limitations']
# Run the real diagnostic mode branch into the patched alternate call, rather
# than testing only the normal helper's bit check.
m=prepared();setup_boot_guard(m);u=m.uc;u.mem_write(ADDR,u32(PHASE['cold']));u.mem_write(0x402296f0,u32(0x00140040));hits=[]
alt=next(h for h in boot_guard_cfg['hooks'] if h['name']=='diagnostic_reject');u.mem_write(alt['site'],bytes.fromhex(alt['replacement']))
for p in [0x4008b05c,0x4008e8b2,0x4009d0d8,0x400ffed0]:u.hook_add(UC_HOOK_CODE,lambda u,pc,n,d:hits.append(hex(pc)),begin=p,end=p)
u.reg_write(UC_M68K_REG_SR,0x201f);u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.emu_start(0x4008d308,0xdeadbee0,count=500)
assert not hits and rd(u,ADDR)==PHASE['failed'] and u.reg_read(UC_M68K_REG_SR)&0xff00==0x2700
out['actual_diagnostic_branch_rejected_before_both_calls']=True
# Deliberately forged boot provenance negative control: copier replay zeros
# LIVE and a matching supplied return lets the seed accept again. This is a
# concrete limit of the design, not evidence that a stock warm caller can do it.
m=prepared();setup_boot_guard(m);u=m.uc;u.mem_write(ADDR,u32(PHASE['live']));u.reg_write(UC_M68K_REG_SR,0x2710);u.reg_write(UC_M68K_REG_A7,RESETSTACK);u.emu_start(0x4029c4b0,0x40001df4,count=100000)
assert rd(u,ADDR)==0 and execute_seed(m,0)==0x40001df4 and rd(u,ADDR)==PHASE['cold']
out['forged_copier_replay_negative_control']={'explicit_host_replay_and_forged_return':True,'seed_accepts_recreated_zero':True,'stock_warm_reachability_proven':False,'fresh_boot_provenance_not_certified':True}
Path('outputs/Digitone-E04-PC-cold-admission-controls.json').write_text(json.dumps(out,indent=2))
print('PASS six seed and five pre-mutation refusal controls')
