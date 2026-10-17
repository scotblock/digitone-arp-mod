from pathlib import Path
exec(Path('work/test-PC-deferred-release-controls.py').read_text().replace('PC_ONLY-deferred-release-overlay','PC_ONLY-resident-deferred-release-overlay').split('\npos=0')[0])
rows=[]
for phase in ['initializing','live','failed']:
 m=fresh();u=m.uc;u.mem_write(STATE,u32(P[phase]));pattern=u32(1)+bytes(12)+struct.pack('>III',1,60,32)+bytes([0xa5])*(defer_cfg['storage_bytes']-28);u.mem_write(defer_cfg['count'],pattern)
 # Direct fallback entry deliberately bypasses setup refusal to characterize
 # the native clear's storage extent; this is not a reachable live reset claim.
 invoke(u,0x47be3400,[158],count=500000)
 assert bytes(u.mem_read(defer_cfg['count'],defer_cfg['storage_bytes']))==pattern
 rows.append({'phase':phase,'direct_actual_fallback_preserves_queue':True,'bypass_is_lifetime_control_not_reachability_proof':True})
m=fresh();u=m.uc;u.mem_write(STATE,u32(P['live']));u.mem_write(defer_cfg['count'],u32(1));before=watched(u);queue=bytes(u.mem_read(defer_cfg['count'],defer_cfg['storage_bytes']))
for h in release_cfg['hooks']:
 if h['name'] in ['normal_setup','setup_body','pool_wrapper','pool_initializer','test_exit_refuse']:
  invoke(u,h['site'],[158],count=10000);assert watched(u)==before and bytes(u.mem_read(defer_cfg['count'],defer_cfg['storage_bytes']))==queue
rows.append({'actual_LIVE_setup_and_initializer_refusals_preserve_queue_and_pool':True})
# Actual recopy is a destructive lifetime boundary, not an ownership guard.
m=fresh();u=m.uc;u.mem_write(defer_cfg['count'],u32(1));m.load(Path('work/os144/PC_ONLY-atomic-storage-main.bin').read_bytes(),0x40000400);invoke_ret=0x40001df4
u.reg_write(UC_M68K_REG_SR,0x271f);u.reg_write(UC_M68K_REG_A7,0x47fdff00);u.emu_start(0x4029c4b0,invoke_ret,count=100000)
assert u.reg_read(UC_M68K_REG_PC)==invoke_ret and bytes(u.mem_read(defer_cfg['count'],defer_cfg['storage_bytes']))==bytes(defer_cfg['storage_bytes'])
rows.append({'native_recopy_clears_pending_queue':True,'actual_warm_recopy_reachability_proven':False})
Path('outputs/Digitone-E04-PC-resident-deferred-lifetime.json').write_text(json.dumps({'PC_only':True,'passed':True,'cases':rows,'limits':['Direct fallback controls characterize actual clear extents while deliberately bypassing the admitted setup boundary. Preservation does not validate old note ownership after a reset.','Recopy requires proven cold provenance or an epoch/invalidation policy; arbitrary later reachability is not excluded.']},indent=2));print('PASS reset preservation, LIVE refusal and recopy lifetime boundary')
