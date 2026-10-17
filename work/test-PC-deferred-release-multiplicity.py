from pathlib import Path
exec(Path('work/test-PC-deferred-release-controls.py').read_text().split('\npos=0')[0])
m=fresh();u=m.uc;u.mem_write(STATE,u32(P['initializing']));ref=0x419952a8+(1*128+60)*4;u.mem_write(ref,u32(2));u.mem_write(0x41994e84,u32(2))
for i in range(3):invoke(u,0x400eabb4,[1,60,32],count=10000)
assert rd(u,defer_cfg['count'])==2 and rd(u,ref)==2 and rd(u,0x41994e84)==2
invoke(u,0x47fa0044,[1],count=100000);assert rd(u,STATE)==P['live'] and rd(u,ref)==0 and rd(u,0x41994e84)==0 and rd(u,defer_cfg['count'])==0
Path('outputs/Digitone-E04-PC-deferred-release-multiplicity.json').write_text(json.dumps({'PC_only':True,'passed':True,'same_track_pitch_reference_count_fixture':2,'three_identical_release_requests_record_two':True,'native_replay_clears_both_stock_reference_counts':True,'limits':['Stock reference counters are supplied as an isolated multiplicity fixture; two actual simultaneous same-pitch producers were not joined here.']},indent=2));print('PASS repeated same-pitch ownership and excess duplicate control')
