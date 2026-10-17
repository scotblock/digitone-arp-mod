from pathlib import Path
exec(Path('work/test-PC-deferred-release-controls.py').read_text().split('\npos=0')[0])
m=fresh();u=m.uc;u.mem_write(STATE,u32(P['initializing']));invoke(u,0x400eabb4,[1,60,32]);assert rd(u,defer_cfg['count'])==1
hits=[]
def fault(u,pc,n,d):hits.append(pc);u.mem_write(defer_cfg['error'],u32(1))
h=u.hook_add(UC_HOOK_CODE,fault,begin=defer_cfg['layout']['stock_internal_release']['address'],end=defer_cfg['layout']['stock_internal_release']['address']);invoke(u,0x47fa0044,[1],count=100000);u.hook_del(h)
assert hits and u.reg_read(UC_M68K_REG_D0)==0 and rd(u,STATE)==P['initializing'] and rd(u,defer_cfg['drain'])==1 and rd(u,defer_cfg['count'])==1
invoke(u,0x47fa0044,[1],count=10000);assert u.reg_read(UC_M68K_REG_D0)==0 and rd(u,STATE)==P['initializing']
Path('outputs/Digitone-E04-PC-deferred-release-failure.json').write_text(json.dumps({'PC_only':True,'passed':True,'injected_error_during_native_drain':True,'no_LIVE_publication':True,'automatic_retry_refused':True,'partial_release_not_rolled_back':True,'actual_exception_cleanup_verified':False,'limits':['Error flag is explicitly injected at a native replay boundary; this is not a physical exception or concurrent callback.','Faulted drain remains closed and latched; recovery is deliberately not implemented.']},indent=2));print('PASS fault during replay cannot publish LIVE or retry automatically')
