from pathlib import Path
exec(Path('work/test-PC-persistent-admission.py').read_text().split('\nout=')[0])
def joined_install(m):
 install(m,PHASE['live'])
 for name in ['input-live','release-reset']:
  spec=json.loads(Path('work/os144/PC_ONLY-'+name+'-overlay.json').read_text());code=Path('work/os144/PC_ONLY-'+name+'-overlay.bin').read_bytes();m.load(code,spec['base']);m.install_isa_patches_scoped(code,spec['base'])
  for h in spec['hooks']:
   assert bytes(m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'],h['name'];m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
s=Path('work/test-PC-deferred-page-lifecycle.py').read_text();s=s[s.index('\nresults=[]'):]
s=s.replace('install(m,True)','joined_install(m)').replace('state_of(m)==baseline',"state_of(m)==baseline and rd(u,ADDR)==PHASE['live']").replace('Digitone-E04-PC-deferred-page-lifecycle.json','Digitone-E04-PC-joined-UI-lifecycle.json').replace("'persistent_latch_installed':False","'persistent_latch_and_input_release_reset_guards_installed':True")
exec(compile(s,'joined-UI-lifecycle','exec'))
