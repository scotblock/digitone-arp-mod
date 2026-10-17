from pathlib import Path
s=Path('work/test-PC-deferred-page-lifecycle.py').read_text()
s=s.replace("exec(Path('work/test-PC-ui-defer-overlay.py').read_text().split('\\nresults=[]')[0])","exec(Path('work/test-PC-persistent-admission.py').read_text().split('\\nout=')[0])")
s=s.replace('install(m,True)','install(m,PHASE[\'live\'])')
s=s.replace('state_of(m)==baseline',"state_of(m)==baseline and rd(u,ADDR)==PHASE['live']")
s=s.replace('Digitone-E04-PC-deferred-page-lifecycle.json','Digitone-E04-PC-persistent-admission-lifecycle.json')
s=s.replace("'persistent_latch_installed':False","'persistent_latch_in_disposable_fixture':True")
s=s.replace('No live IRQ concurrency, hardware behavior or persistent admission certification.','Guest guard reads persistent LIVE across native close/re-entry/destruction; startup seed/provenance, global ownership, IRQ concurrency and hardware remain unproven.')
exec(compile(s,'persistent-admission-lifecycle','exec'))
