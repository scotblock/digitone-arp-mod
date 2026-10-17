from pathlib import Path
exec(Path('work/test-PC-deferred-release-controls.py').read_text().split('\npos=0')[0])
m=fresh();u=m.uc;u.mem_write(STATE,u32(P['initializing']));invoke(u,0x400eabb4,[1,60,32]);events=[]
def store(u,access,a,n,v,d):
 if a<STATE+4 and a+n>STATE:events.append({'value':hex(v),'IPL':(u.reg_read(UC_M68K_REG_SR)>>8)&7,'pending_count':rd(u,defer_cfg['count']),'drain':rd(u,defer_cfg['drain'])})
h=u.hook_add(UC_HOOK_MEM_WRITE,store);invoke(u,0x47fa0044,[1],sr=0x231f,count=100000);u.hook_del(h)
assert events==[{'value':hex(P['live']),'IPL':7,'pending_count':0,'drain':0}] and u.reg_read(UC_M68K_REG_SR)==0x231f
Path('outputs/Digitone-E04-PC-deferred-release-publication.json').write_text(json.dumps({'PC_only':True,'passed':True,'phase_writes':events,'incoming_full_SR_restored':True,'limits':['Native release plus final store executes without guest timers or competing scheduled input; physical interrupt/cache effects remain unverified.']},indent=2));print('PASS drain completes before masked LIVE store')
