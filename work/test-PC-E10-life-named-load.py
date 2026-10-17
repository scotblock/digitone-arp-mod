"""Load the native-panel-created project after lifecycle-image cold startup."""
from pathlib import Path
import json
proof=json.loads(Path('outputs/Digitone-E10-PC-bound-panel-patterns.json').read_text());assert proof['passed']
expected=[bytes.fromhex(x) for x in proof['expected_records']]
source=Path('work/test-PC-E10-storage-cold-reload.py').read_text(encoding='utf-8')
anchor="exec(compile(prefix,'E10-cold-reload-definitions','exec'))"
changes=[('outputs/Digitone-E09A-PC-path-layout.json','work/os144/PC_ONLY-E10-life-full-layout.json'),("folder/'E09A-PC-install-layout.json'","folder/'PC_ONLY-E10-life-layout.json'"),('outputs/Digitone-E09A-PC-startup-comparison.json','outputs/Digitone-E10-PC-life-startup.json'),("folder/'E09A-PC-layout-payload.bin'","folder/'PC_ONLY-E10-life-payload.bin'"),("folder/'E09A-PC-layout-main.bin'","folder/'PC_ONLY-E10-life-main.bin'")]
injection=''.join('prefix=prefix.replace('+repr(a)+','+repr(b)+')\n' for a,b in changes)
old="    for region in native['data_regions']:";new=old+"\n        if region['name'] in ['E10_persistence_metadata','E10_pattern_binding_metadata','E10_lifecycle_metadata']:continue"
injection+='prefix=prefix.replace('+repr(old)+','+repr(new)+')\n'
source=source.replace(anchor,injection+anchor).replace('outputs/Digitone-E10-PC-storage-cold-startup.json','outputs/Digitone-E10-PC-life-startup.json').replace('work/E10-storage-cold-reload','work/E10-life-named-load').replace('outputs/E10-storage-cold-reload-','outputs/E10-life-named-load-').replace('outputs/Digitone-E10-PC-storage-cold-reload.json','outputs/Digitone-E10-PC-life-named-load.json')
source=source.replace('data==record_bytes(slot)',"data==(expected[slot] if slot<2 else bytes(32))")
needle=" s.ev['esdhc'].card.flush();preserved(s);out['passed']=True"
extra="""
 assert bytes(s.m.uc.mem_read(native['E10']['bank'],64))==b''.join(expected)
 Z=native['lifecycle']['meta'];PM=native['persistence']['meta']
 for _ in range(24):
  if rd(s.m.uc,Z)==0x4d434831 and rd(s.m.uc,Z+4)==rd(s.m.uc,PM+12):break
  s.run_ms(250)
 assert rd(s.m.uc,Z)==0x4d434831 and rd(s.m.uc,Z+4)==rd(s.m.uc,PM+12)
 # The snapshot format does not preserve EMAC mode. Do not checkpoint an
 # interrupted fractional-audio context: stock code subsequently asserts it.
 from unicorn.m68k_const import UC_M68K_REG_SR
 for _ in range(1000):
  s.run_ms(1)
  if s.m.uc.reg_read(UC_M68K_REG_SR)&0x0700<=0x0100:break
 assert s.m.uc.reg_read(UC_M68K_REG_SR)&0x0700<=0x0100, ('No task-level checkpoint boundary',hex(s.pc),hex(s.m.uc.reg_read(UC_M68K_REG_SR)))
 out['task_level_checkpoint_SR']=s.m.uc.reg_read(UC_M68K_REG_SR)
 from emu.snapshot import save
 checkpoint='work/E10-life-named-load/native-loaded.snap'
 save(s.m,checkpoint,components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'))
 out.update(native_loaded_snapshot=checkpoint,private_card=paths.card,expected_records=[x.hex() for x in expected],retained_mirror_generation_bound=True)
 s.ev['esdhc'].card.flush();preserved(s);out['passed']=True
"""
assert needle in source;source=source.replace(needle,extra)
exec(compile(source,'E10-life-native-named-load','exec'))
p=Path('outputs/Digitone-E10-PC-life-named-load.json');r=json.loads(p.read_text());assert r['passed']
r['limits']=['Copier-installed lifecycle image; the named file contains records previously created by the native editor. No record/bank/code/hook data are host-inserted.','Cold direct MAIN plus native named load, not a physical reboot or an E10 packaged loader.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
