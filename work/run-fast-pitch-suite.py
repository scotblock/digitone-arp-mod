import pathlib,subprocess,sys,os,json,concurrent.futures,time
jobs=[('prefix-stock','stock',False,False),('prefix-sham','sham',True,False),('prefix-pitch-only','stock_changed',False,False),('prefix-fixed','all_fixed',True,False),('prefix-full','all',True,False),('long-stock','stock',False,True),('long-fixed','all_fixed',True,True),('long-full','all',True,True)]
def run(job):
 name,mode,fast,long=job;env=os.environ.copy()
 env.update(STRESS_MODE=mode,FAST_PITCH=str(int(fast)),LONG_PLAYBACK=str(int(long)),DEADLINE_FSYS='264000000',MEM_FILL='40',MEM_WRITEBACK='32',MEM_BEAT='8',MEM_CONTENTION='1',STRESS_PATTERN_TWO='1',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='1',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-fast-pitch-{name}.json')
 for key in ['NEUTRAL_HELPER_MEMORY','NEUTRAL_HELPER_COMPUTE','NEUTRAL_PITCH_FETCH']:env.pop(key,None)
 print('START',name,flush=True)
 with pathlib.Path(f'work/fast-pitch-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-fast-pitch-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 result=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text())
 assert rc==0 and result['failure'] is None,(name,result.get('failure'))
 q=result['runs'][0];assert q['clock']['decode_mismatches']==0 and q['halted'] is None
 print('DONE',name,'ms',q['ms'],'stale',q['DMA_summary']['captures_with_unfresh_words'],'minimum margin',q['DMA_summary']['minimum_margin_us'],flush=True)
 return name
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for result in pool.map(run,jobs):pass
print('ALL CASES COMPLETE',flush=True)
