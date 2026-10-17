import pathlib,json
for fn in ['Digitone-full-handler-transition-execution-results.json','Digitone-outer-mode-entry-complete-results.json','Digitone-receive-full-handler-results.json']:
 r=json.loads(pathlib.Path('outputs',fn).read_text());print(fn,len(r['checks']),len(r['cases']),sum(len(c.get('entry_steps',[]))+len(c.get('handler_steps',[]))+len(c.get('outer_steps',[]))+len(c.get('steps',[])) for c in r['cases']))
