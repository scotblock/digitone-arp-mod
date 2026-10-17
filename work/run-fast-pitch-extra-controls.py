import pathlib,subprocess,sys,os,json,concurrent.futures
jobs=[('prefix-context-only','context_only',None),('prefix-memory-neutral','all_fixed','NEUTRAL_HELPER_MEMORY'),('prefix-compute-neutral','all_fixed','NEUTRAL_HELPER_COMPUTE'),('prefix-fetch-neutral','all_fixed','NEUTRAL_PITCH_FETCH')]
def run(job):
 name,mode,ablation=job;env=os.environ.copy()
 env.update(STRESS_MODE=mode,FAST_PITCH='1',LONG_PLAYBACK='0',DEADLINE_FSYS='264000000',MEM_FILL='40',MEM_WRITEBACK='32',MEM_BEAT='8',MEM_CONTENTION='1',STRESS_PATTERN_TWO='1',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='1',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-fast-pitch-{name}.json')
 for key in ['NEUTRAL_HELPER_MEMORY','NEUTRAL_HELPER_COMPUTE','NEUTRAL_PITCH_FETCH']:env.pop(key,None)
 if ablation:env[ablation]='1'
 print('START',name,flush=True)
 with pathlib.Path(f'work/fast-pitch-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-fast-pitch-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 r=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text());assert rc==0 and r['failure'] is None,(name,r.get('failure'))
 q=r['runs'][0];assert q['clock']['decode_mismatches']==0 and q['halted'] is None
 print('DONE',name,'stale',q['DMA_summary']['captures_with_unfresh_words'],'margin',q['DMA_summary']['minimum_margin_us'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,jobs))
