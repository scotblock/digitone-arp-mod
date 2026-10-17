from pathlib import Path
import json
resident_panel_reader=Path.read_text
spec=json.loads(resident_panel_reader(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.json')))
def resident_panel_read(path,*args,**kwargs):
 text=resident_panel_reader(path,*args,**kwargs)
 if path.name=='probe-PC-joined-UI-panel.py':
  text=text.replace('Digitone-E04-PC-release-reset-startup-startup.json','Digitone-E04-PC-resident-deferred-startup-startup.json')
  text=text.replace("assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['stock'];", "assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex() in [h['stock'],h['replacement']];")
 return text
text=resident_panel_reader(Path('work/test-PC-deferred-release-panel.py'))
text=text.replace('PC_ONLY-deferred-release-overlay','PC_ONLY-resident-deferred-release-overlay').replace('Digitone-E04-PC-deferred-release-panel.json','Digitone-E04-PC-resident-deferred-panel.json')
text=text.replace("s.m.ensure(deferred_spec['count']);s.m.uc.mem_write(deferred_spec['count'],bytes(deferred_spec['storage_bytes']))", "s.m.ensure(deferred_spec['count']);assert bytes(s.m.uc.mem_read(deferred_spec['count'],deferred_spec['storage_bytes']))==bytes(deferred_spec['storage_bytes'])")
text=text.replace("==h['previous'];", " in [h['previous'],h['replacement']];")
anchor="   points={'panel_IRQ'"
# This anchor is inside source replacement string and must be installed into
# the probe source itself, rather than the outer composition script.
watch="""   from unicorn import UC_HOOK_MEM_WRITE
   r['queue_writers']={};r['queue_canaries']=bytes(s.m.uc.mem_read(spec['count']-16,16))+bytes(s.m.uc.mem_read(spec['count']+spec['storage_bytes'],16))
   def watch(u,access,address,length,value,data):
    if not (0x40000000<=address<0x80000000):return
    canonical=0x40000000+(address-0x40000000)%0x08000000
    if canonical<spec['count']+spec['storage_bytes'] and canonical+length>spec['count']:
     pc=u.reg_read(UC_M68K_REG_PC);r['queue_writers'][hex(pc)]=r['queue_writers'].get(hex(pc),0)+1
     assert spec['base']<=pc<spec['base']+spec['bytes'],hex(pc)
   for alias in range(8):
    base=spec['count']+alias*0x08000000;s.m.uc.hook_add(UC_HOOK_MEM_WRITE,watch,begin=base-64,end=base+spec['storage_bytes']+63)
"""
base_reader=resident_panel_read
def with_watch(path,*args,**kwargs):
 t=base_reader(path,*args,**kwargs)
 if path.name=='probe-PC-joined-UI-panel.py':
  assert anchor in t;t=t.replace(anchor,watch+anchor)
  t=t.replace("  r.update(passed=s.halted is None,halted=s.halted)","  assert bytes(s.m.uc.mem_read(spec['count']-16,16))+bytes(s.m.uc.mem_read(spec['count']+spec['storage_bytes'],16))==r.pop('queue_canaries')\n  r['adjacent_canaries_preserved']=True\n  r.update(passed=s.halted is None,halted=s.halted)")
 return t
Path.read_text=with_watch
try:exec(compile(text,'resident-deferred-panel','exec'))
finally:Path.read_text=resident_panel_reader
