import os,pathlib,subprocess,sys,concurrent.futures,json
jobs=[('prepared-stock-normal','stock',40,32,8),('prepared-full-normal','all',40,32,8),('prepared-stock-150pct','stock',60,48,12),('prepared-full-150pct','all',60,48,12),('prepared-stock-double','stock',80,64,16),('prepared-full-double','all',80,64,16)]
def run(job):
 name,mode,fill,wb,beat=job;env=os.environ.copy()
 env.update(STRESS_MODE=mode,LONG_PLAYBACK='0',MEM_FILL=str(fill),MEM_WRITEBACK=str(wb),MEM_BEAT=str(beat),MEM_CONTENTION='1',STRESS_PATTERN_TWO='0',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='0',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-dma-restart-{name}.json')
 print('START',name,flush=True)
 with pathlib.Path(f'work/dma-restart-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-prepared-dma-timing-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 r=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text());print('DONE',name,'rc',rc,'failure',r['failure'],flush=True)
 return {'name':name,'returncode':rc,'failure':r['failure']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:results=list(p.map(run,jobs))
pathlib.Path('outputs/Digitone-dma-restart-prepared-status.json').write_text(json.dumps(results,indent=2))
