"""Direct-MAIN cold -> logo -> UI using the integrated E10 copier image.

E09A's unchanged container supplies stock DSP/resources only. This is explicitly
NOT loader-derived E10 state and does not create a firmware container.
"""
from pathlib import Path
import json
old=json.loads(Path('outputs/Digitone-E09A-PC-path-layout.json').read_text())
new=json.loads(Path('work/os144/PC_ONLY-E10-startup-layout.json').read_text())
regions={r['base']:r for r in old['regions']}
regions.update({r['base']:r for r in new['regions']})
components={r['base']:r for r in old['components']}
components.update({r['base']:r for r in new['regions']+new['data_regions']})
cfg={**old,**new,'regions':list(regions.values()),'components':list(components.values())}
Path('work/os144/PC_ONLY-E10-startup-full-layout.json').write_text(json.dumps(cfg,indent=2))
source=Path('work/test-E07-PC-startup.py').read_text().replace('E07','E10')
source=source.replace("['stock_default','stock_restored','E10_default','E10_restored','E10_disabled']","['E10_restored']")
source=source.replace('outputs/Digitone-E10-PC-candidate-layout.json','work/os144/PC_ONLY-E10-startup-full-layout.json')
source=source.replace('work/os144/E10-PC-payload.bin','work/os144/PC_ONLY-E10-startup-payload.bin')
source=source.replace('work/os144/E10-PC-main.bin','work/os144/PC_ONLY-E10-startup-main.bin')
source=source.replace('work/os144/E10-PC-candidate.syx','work/os144/E09A-PC-path-candidate.syx')
source=source.replace('Digitone-E10-PC-startup-comparison.json','Digitone-E10-PC-integrated-startup.json')
extra="  row['E10_startup_status']=int.from_bytes(m.uc.mem_read(cfg['E10_status'],4),'big')\n  assert row['E10_startup_status']==1\n  assert bytes(m.uc.mem_read(cfg['E10']['bank'],4096))==bytes(4096)\n  assert int.from_bytes(m.uc.mem_read(cfg['E10']['state'],4),'big')==0x4d535131\n  save(m,paths.cold"
anchor="exec(compile(s,'E10-packaged-startup','exec'))"
assert anchor in source
source=source.replace(anchor,"s=s.replace("+repr('  save(m,paths.cold')+','+repr(extra)+")\n"+anchor)
exec(compile(source,'E10-direct-MAIN-native-startup','exec'))
r=json.loads(Path('outputs/Digitone-E10-PC-integrated-startup.json').read_text())
r.update(firmware_container_created=False,loader_derived_E10_state=False,helpers_host_loaded=False,native_project_persistence=False)
r['limits'].append('Unchanged E09A container supplies DSP/resources; E10 MAIN is directly loaded. This does not prove an E10 packaged loader path.')
Path('outputs/Digitone-E10-PC-integrated-startup.json').write_text(json.dumps(r,indent=2))
