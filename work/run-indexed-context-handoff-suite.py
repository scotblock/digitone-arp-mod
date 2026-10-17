import pathlib,subprocess,sys,os,json
for mode,scaled in [('all',False),('stock',False),('all',True),('stock',True)]:
 env=os.environ.copy();env.update(HANDOFF_MODE=mode,SCALE_HANDOFF=str(int(scaled)))
 name=mode+('-scaled' if scaled else '')
 with pathlib.Path('work/indexed-context-handoff-'+name+'.log').open('w') as log:
  subprocess.run([sys.executable,'work/test-indexed-context-handoff.py'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 result=json.loads(pathlib.Path('outputs/Digitone-indexed-context-handoff-'+name+'.json').read_text())
 assert result['failure'] is None
 print('DONE',name,flush=True)
subprocess.run([sys.executable,'work/summarize-indexed-context-handoff.py'],check=True)
