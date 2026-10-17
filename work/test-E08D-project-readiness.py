"""Native saved-project reload with E08D owner identities observed."""
from pathlib import Path
source=Path('work/test-E08C-packaged-project-controls.py').read_text().replace('E08C','E08D')
anchor="Path('work/generated-E08D-packaged-project-controls.py').write_text(s)"
extra=r'''
s=s.replace("out['steps'].append({'MIDI_settings_word':", "out['steps'].append({'owner':hex(rd(s.m.uc,cfg['state']+336)),'request_owner':hex(rd(s.m.uc,cfg['state']+340)),'UI_data':hex(rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0xff8+16)),'stock_kit':hex(rd(s.m.uc,0x419c5b10)),'MIDI_settings_word':")
s=s.replace(" out['offers']=[]",r"""
 out['ownership_writes']=[]
 def ownership_write(u,access,a,n,value,d):
  out['ownership_writes'].append({'phase':phase,'address':hex(a),'value':hex(value),'writer':hex(u.reg_read(UC_M68K_REG_PC))})
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,ownership_write,begin=cfg['state']+336,end=cfg['state']+343)
 out['offers']=[]
""")
'''
assert anchor in source;source=source.replace(anchor,extra+'\n'+anchor)
exec(compile(source,'E08D-project-readiness','exec'))
