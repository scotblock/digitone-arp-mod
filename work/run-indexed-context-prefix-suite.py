"""Repeat principal timing controls from the executed-loader startup snapshot."""
import pathlib,subprocess,sys,os,json,concurrent.futures
jobs=[('prefix-stock','stock',False),('prefix-fixed','all_fixed',False),('prefix-full','all',False)]
def run(job):
 name,mode,long=job;env=os.environ.copy()
 env.update(STRESS_MODE=mode,LONG_PLAYBACK=str(int(long)),DEADLINE_FSYS='264000000',MEM_FILL='40',MEM_WRITEBACK='32',MEM_BEAT='8',MEM_CONTENTION='1',STRESS_PATTERN_TWO='1',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='1',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-indexed-context-timing-{name}.json')
 for key in ['NEUTRAL_HELPER_MEMORY','NEUTRAL_HELPER_COMPUTE','NEUTRAL_PITCH_FETCH']:env.pop(key,None)
 print('START',name,flush=True)
 with pathlib.Path(f'work/indexed-context-timing-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-indexed-context-timing-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 r=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text())
 assert rc==0 and r['failure'] is None,(name,r.get('failure'))
 q=r['runs'][0];assert q['clock']['decode_mismatches']==0 and q['halted'] is None
 assert all(q['storage_checks'].values())
 print('DONE',name,'ms',q['ms'],'stale',q['DMA_summary']['captures_with_unfresh_words'],'margin',q['DMA_summary']['minimum_margin_us'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,jobs))
print('ALL PRINCIPAL CONTROLS COMPLETE',flush=True)


