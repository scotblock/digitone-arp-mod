"""Render the nested local runner, then change only fresh pattern settings."""
import pathlib,builtins,os
os.environ.update(CACHE_CONTEXT_MODE='fixed',CACHE_REFRESH='0',ARP_CONTROL='no-delay')
original=builtins.compile
def render(source,filename,mode,*args,**kwargs):
 if filename=='indexed-context-handoff':
  source="CACHE_MODE='fixed'\n"+source
  target=' select_pattern(2);copy_source=rd(session.m.uc,0x41342150)'
  assert target in source
  prep=" for track in range(4):\n  session.m.uc.mem_write(0x407c61e9+track*0x3d0+0x3cb,bytes([59]))\n  session.m.uc.mem_write(0x407c61e9+track*0x3d0+0x3ce,bytes([5]))\n"
  source=source.replace(target,prep+target)
  source=source.replace('actual_old+track*0x3d0+0x3cb,bytes([61])','actual_old+track*0x3d0+0x3cb,bytes([59])')
  source=source.replace('actual_old+track*0x3d0+0x3ce,bytes([0])','actual_old+track*0x3d0+0x3ce,bytes([5])')
  source=source.replace("'old_root':61,'old_raw_scale':0","'old_root':59,'old_raw_scale':5")
  source=source.replace('cache-context-fixed-no-delay.json','cache-context-fresh-settings.json')
  pathlib.Path('work/test-cache-context-fresh-rendered.py').write_text(source)
  raise SystemExit('Fresh-setting PC runner rendered')
 return original(source,filename,mode,*args,**kwargs)
builtins.compile=render
exec(pathlib.Path('work/test-cache-context-crossing.py').read_text())
