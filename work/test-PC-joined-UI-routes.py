from pathlib import Path
exec(Path('work/test-PC-persistent-admission.py').read_text().split('\nout=')[0])
original_ui_install=install
# All experiments here are LIVE; setup intentionally uses the retained native
# page fixtures, then both existing input and reset overlays are joined.
def install(m,live):
 original_ui_install(m,PHASE['live'])
 for name in ['input-live','release-reset']:
  spec=json.loads(Path('work/os144/PC_ONLY-'+name+'-overlay.json').read_text());code=Path('work/os144/PC_ONLY-'+name+'-overlay.bin').read_bytes();m.load(code,spec['base']);m.install_isa_patches_scoped(code,spec['base'])
  for h in spec['hooks']:
   assert bytes(m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'],h['name'];m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
s=Path('work/test-PC-ui-defer-overlay.py').read_text();s=s[s.index('\nresults=[]'):]
s=s.replace("[('audio',True),('audio',False),('ordinary',True),('null',True)]","[('audio',True),('ordinary',True),('null',True)]").replace('guardcfg','admission_cfg').replace('len(blob)','len(admission_blob)').replace('Digitone-E04-PC-ui-defer-overlay-tests.json','Digitone-E04-PC-joined-UI-routes.json').replace("'persistent_latch_installed':False","'persistent_UI_input_release_reset_guards_installed':True")
exec(compile(s,'joined-UI-routes','exec'))
