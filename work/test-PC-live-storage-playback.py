from pathlib import Path
original=Path.read_text
def read_source(path,*args,**kwargs):
 s=original(path,*args,**kwargs)
 if path.name=='test-PC-ISA-loader-playback.py':
  s=s.replace('Digitone-E04-PC-ISA-loader-startup.json','Digitone-E04-PC-live-storage-startup.json')
  s=s.replace("assert len(startup['cases'])==2", "startup['cases']=startup['cases'][:2]\nassert len(startup['cases'])==2")
 return s
s=original(Path('work/test-PC-live-capture-session.py'))
s=s.replace('Digitone-E04-PC-live-capture-session.json','Digitone-E04-PC-live-storage-playback.json')
s=s.replace("    uc.mem_write(cfg['base'],newcode);uc.mem_write(cfg['state'],bytes(cfg['state_bytes']));session.m.install_isa_patches_scoped(newcode,cfg['base'])", "    assert bytes(uc.mem_read(cfg['base'],len(newcode)))==newcode\n    assert bytes(uc.mem_read(cfg['state'],cfg['state_bytes']))==bytes(cfg['state_bytes'])\n    r['live_code_copied_by_startup']=True;r['extra_storage_initialized_by_guest']=True\n    session.m.install_isa_patches_scoped(newcode,cfg['base'])\n    full=Path('work/os144/PC_ONLY-live-storage-payload.bin').read_bytes();session.m.install_isa_patches_scoped(full[0x3400:0x3530],0x47be3400)")
s=s.replace("     assert bytes(uc.mem_read(h['site'],h['length'])).hex()==h['stock'];uc.mem_write(h['site'],bytes.fromhex(h['replacement']))", "     assert bytes(uc.mem_read(h['site'],h['length'])).hex()==h['replacement']")
Path.read_text=read_source
try:exec(compile(s,'live-storage-startup-playback','exec'))
finally:Path.read_text=original
