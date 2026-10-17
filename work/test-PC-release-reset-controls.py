from pathlib import Path
exec(Path('work/test-PC-input-live-controls.py').read_text().split('\nout=')[0])
release_cfg=json.loads(Path('work/os144/PC_ONLY-release-reset-overlay.json').read_text());release_blob=Path('work/os144/PC_ONLY-release-reset-overlay.bin').read_bytes()
def install_release(m):
 m.load(release_blob,release_cfg['base']);m.install_isa_patches_scoped(release_blob,release_cfg['base'])
 for h in release_cfg['hooks']:
  assert bytes(m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'],h['name']
  m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
def watched(u):return fingerprint(u)+hashlib.sha256(bytes(u.mem_read(0x419afff4,0x200))+bytes(u.mem_read(0x402a0e50,4))+bytes(u.mem_read(0x40236788,4))+bytes(u.mem_read(0x41392fa4,4))).hexdigest()
p=0
while p<len(release_blob):
 ins=cfisa.decode(lambda off:int.from_bytes(release_blob[p+off:p+off+2],'big'),release_cfg['base']+p)
 assert not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(release_blob[p:p+2],'big'))
 p+=ins.length
assert p==len(release_blob)
report={'PC_only':True,'denials':[],'cold_pool_pairs':[],'ISA_audit_passed':True}
for phase in ['cold','initializing','live','failed']:
 for h in release_cfg['hooks']:
  if h['name']=='command_exit_cleanup' or (phase=='live' and h['name'] in ['note_off','sustain_set','sustain_release']):continue
  m=restored('work/startup-producer-order-E04_restored/producer-0x4008d3ec.snap');install_inputs(m);install_release(m);u=m.uc;u.mem_write(STATE,u32(P[phase]));before=watched(u);saved=regs(u)
  invoke(u,h['site'],[0]*8,count=2000)
  assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0 and regs(u)==saved and u.reg_read(UC_M68K_REG_SR)==0x201f and watched(u)==before
  report['denials'].append({'phase':phase,'entry':h['name'],'no_storage_or_flags_mutation':True,'CPU_SR_preserved':True})
# Full pool wrapper executes actual stock initializer and cleanup; native
# return reproduced to keep its initializer's existing caller contract.
for phase in ['initializing']:
 pairs=[]
 for guarded in [False,True]:
  m=restored('work/startup-producer-order-E04_restored/producer-0x4008d3ec.snap');install_inputs(m);u=m.uc
  if guarded:install_release(m)
  u.mem_write(STATE,u32(P[phase]));invoke(u,0x4009c5a0,[],ret=0x4009c5d8,count=500000)
  assert u.reg_read(UC_M68K_REG_PC)==0x4009c5d8 and rd(u,0x47be1010)==1
  pairs.append({'state':watched(u),'regs':regs(u),'SR':u.reg_read(UC_M68K_REG_SR),'SP':u.reg_read(UC_M68K_REG_A7)})
 assert pairs[0]==pairs[1]
 report['cold_pool_pairs'].append({'full_pool_wrapper_and_initializer_parity':True})
report['passed']=True;Path('outputs/Digitone-E04-PC-release-reset-controls.json').write_text(json.dumps(report,indent=2));print('PASS',len(report['denials']),'denials and cold pool pair')
