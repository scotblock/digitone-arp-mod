"""Independent timing controls, inherited revised startup, no candidate injection."""
import pathlib,subprocess,sys,os,json,concurrent.futures
jobs=[('prefix-stock','stock',False,40,32,8),('prefix-fixed','all_fixed',False,40,32,8),('prefix-full','all',False,40,32,8),('sustained-stock','stock',True,40,32,8),('sustained-full','all',True,40,32,8),('sustained-full-slow-memory','all',True,80,64,16)]
def run(job):
 name,mode,long,fill,wb,beat=job;env=os.environ.copy()
 env.update(STRESS_MODE=mode,LONG_PLAYBACK=str(int(long)),DEADLINE_FSYS='264000000',MEM_FILL=str(fill),MEM_WRITEBACK=str(wb),MEM_BEAT=str(beat),MEM_CONTENTION='1',STRESS_PATTERN_TWO='1',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='0',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-cache-startup-timing-{name}.json')
 for key in ['NEUTRAL_HELPER_MEMORY','NEUTRAL_HELPER_COMPUTE','NEUTRAL_PITCH_FETCH','EXTENDED_HOLD']:env.pop(key,None)
 if long:env['EXTENDED_HOLD']='1'
 print('START',name,flush=True)
 with pathlib.Path(f'work/cache-startup-timing-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-cache-context-timing-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 r=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text());assert rc==0 and r['failure'] is None,(name,r.get('failure'))
 q=r['runs'][0];assert q['clock']['decode_mismatches']==0 and q['halted'] is None and all(q['storage_checks'].values())
 assert not q['candidate_fixture'];print('DONE',name,'ms',q['ms'],'copy calls',len(q['cache_copy_calls']),'native quantizers',len(q['quantizer_calls']),'stale',q['DMA_summary']['captures_with_unfresh_words'],'margin',q['DMA_summary']['minimum_margin_us'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,jobs))
print('SIX TIMING CASES COMPLETE',flush=True)
