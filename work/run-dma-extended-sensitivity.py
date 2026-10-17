"""Repeat voice workload at two memory-cost sensitivities after restart fix."""
import os,pathlib,subprocess,sys,json,concurrent.futures
jobs=[('stock-150pct','stock',60,48,12),('full-150pct','all',60,48,12),('stock-double-voices','stock',80,64,16),('full-double-voices','all',80,64,16)]
def run(job):
 name,mode,fill,wb,beat=job;env=os.environ.copy()
 env.update(STRESS_MODE=mode,LONG_PLAYBACK='1',MEM_FILL=str(fill),MEM_WRITEBACK=str(wb),MEM_BEAT=str(beat),MEM_CONTENTION='1',STRESS_PATTERN_TWO='1',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='0',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-dma-restart-{name}.json')
 for k in ['NEUTRAL_HELPER_MEMORY','NEUTRAL_HELPER_COMPUTE','NEUTRAL_PITCH_FETCH','EXTENDED_HOLD']:env.pop(k,None)
 print('START',name,flush=True)
 with pathlib.Path(f'work/dma-restart-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-cache-context-timing-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 r=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text());print('DONE',name,'rc',rc,'failure',r['failure'],'ms',r['runs'][0].get('ms'),flush=True)
 return {'name':name,'returncode':rc,'failure':r['failure']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:results=list(p.map(run,jobs))
pathlib.Path('outputs/Digitone-dma-restart-extended-status.json').write_text(json.dumps(results,indent=2))
