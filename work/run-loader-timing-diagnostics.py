"""Additional short controls for the newly observed loader-derived stale read."""
exec(open('work/run-loader-timing-suite.py').read().split('with concurrent.futures')[0])
jobs=[('prefix-sham','sham',None),('prefix-pitch-only','stock_changed',None),('prefix-context-only','context_only',None),('prefix-memory-neutral','all_fixed','NEUTRAL_HELPER_MEMORY'),('prefix-compute-neutral','all_fixed','NEUTRAL_HELPER_COMPUTE'),('prefix-fetch-neutral','all_fixed','NEUTRAL_PITCH_FETCH')]
for name,mode,ablation in jobs:
 env=os.environ.copy();env.update(STRESS_MODE=mode,LONG_PLAYBACK='0',DEADLINE_FSYS='264000000',MEM_FILL='40',MEM_WRITEBACK='32',MEM_BEAT='8',MEM_CONTENTION='1',STRESS_PATTERN_TWO='1',STRESS_CAPTURE_ALL='1',DEADLINE_VALID_CONTEXT='1',DEADLINE_SCALE='1',DEADLINE_OUT=f'outputs/Digitone-loader-timing-{name}.json')
 for key in ['NEUTRAL_HELPER_MEMORY','NEUTRAL_HELPER_COMPUTE','NEUTRAL_PITCH_FETCH']:env.pop(key,None)
 if ablation:env[ablation]='1'
 print('START',name,flush=True)
 with pathlib.Path(f'work/loader-timing-{name}.log').open('w') as f:
  rc=subprocess.run([sys.executable,'work/run-loader-timing-case.py'],env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).returncode
 r=json.loads(pathlib.Path(env['DEADLINE_OUT']).read_text());assert rc==0 and r['failure'] is None,(name,r.get('failure'))
 q=r['runs'][0];assert q['clock']['decode_mismatches']==0 and q['halted'] is None and all(q['storage_checks'].values())
 print('DONE',name,'stale',q['DMA_summary']['captures_with_unfresh_words'],'margin',q['DMA_summary']['minimum_margin_us'],flush=True)
