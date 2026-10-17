"""Repeat panel editing and native project persistence without PC code overlays."""
from pathlib import Path

driver = Path('work/test-E08-native-M1-controls.py').read_text()
replacement = r'''
# s is the fully generated panel/save/reload scenario. Point it at the new
# package and its own loader-derived UI state, without using the old warm RAM.
for old,new in [
    ('E08-PC-path-candidate.syx','E08C-PC-path-candidate.syx'),
    ('Digitone-E08-PC-startup-comparison.json','Digitone-E08C-PC-startup-comparison.json'),
    ('Digitone-E08-PC-path-layout.json','Digitone-E08C-PC-path-layout.json'),
    ('E08-PC-layout-payload.bin','E08C-PC-layout-payload.bin'),
    ('E08-controls-warm.snap','E08C-controls-warm.snap'),
    ('Digitone-E08-native-M1-controls.json','Digitone-E08C-packaged-project-controls.json'),
    ('E08-native-M1-controls-','E08C-packaged-project-controls-')]:
    s=s.replace(old,new)
# Always start with this package's fresh startup checkpoint. Do not inherit a
# previously edited warm session when checking packaged initialization.
s=s.replace("if warm.exists():case['ui_snapshot']=str(warm.resolve())", "# fresh packaged startup is required")
s=s.replace('if not warm.exists():', 'if True:')
# The old overlay decoder setup defines globals named payload/main for its
# historical E04 audit. It is unnecessary here: package/startup already checked
# the ISA, and those old globals would corrupt this readback's expectations.
s='\n'.join(line for line in s.split('\n') if "exec(Path('work/audit-E04-startup-ISA.py')" not in line)
s=s.replace("else:s.run_ms(200);s.tap(s.code('STOP'),hold_ms=100,after_ms=100)",
            "else:s.run_ms(200)\n s.tap(s.code('STOP'),hold_ms=100,after_ms=100)")
start=s.index(" for f in ['settings-accessors','settings-codec-bridge','M1-controls']:")
end=s.index(' def encoder(u,pc,n,d):',start)
s=s[:start]+r"""
 out['helpers_host_loaded']=False;out['hooks_host_patched']=False;out['M1_initializer_host_called']=False
 for region in cfg['regions']:
  if region['base']<0x47be0000:continue
  expected=payload[region['base']-0x47be0000:region['base']-0x47be0000+region['bytes']]
  assert bytes(s.m.uc.mem_read(region['base'],region['bytes']))==expected,region['name']
 for hook in cfg['hooks']:
  assert bytes(s.m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['replacement'],hook
"""+s[end:]
Path('work/generated-E08C-packaged-project-controls.py').write_text(s)
exec(compile(s,'E08C-packaged-project-controls','exec'))
'''
anchor="exec(compile(s,'E08-native-M1-device-controls','exec'))"
assert anchor in driver
driver = driver.replace(anchor, replacement)
exec(compile(driver,'E08C-controls-scenario-driver','exec'))
