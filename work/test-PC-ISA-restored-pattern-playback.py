from pathlib import Path
import json
s=Path('work/test-PC-ISA-loader-playback.py').read_text()
old=json.loads(Path('outputs/Digitone-E04-PC-ISA-loader-playback.json').read_text())
if not Path('outputs/Digitone-E04-PC-ISA-empty-pattern-controls.json').exists():
 Path('outputs/Digitone-E04-PC-ISA-empty-pattern-controls.json').write_text(json.dumps(old,indent=2))
Path('outputs/Digitone-E04-PC-ISA-late-pattern-fixture-controls.json').write_text(json.dumps(old,indent=2))
extra=r'''
default=startup['cases'][0]
root=Path(default['ui_snapshot']).parents[2]
paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
reference=Session(default['ui_snapshot'],syx=str(syx),ddr=0x08000000)
try:
 reference.tap(reference.code('STOP'),hold_ms=100,after_ms=100)
 reference.press(reference.code('PTN'));reference.run_ms(100);reference.tap(reference.code('2'),hold_ms=100,after_ms=100);reference.release(reference.code('PTN'));reference.run_ms(300)
 template_back=rd(reference.m.uc,0x4138f214)
 template=bytes(reference.m.uc.mem_read(template_back,4*0x3d0))
finally:reference.close()
out['cases']=[c for c in json.loads(Path('outputs/Digitone-E04-PC-ISA-empty-pattern-controls.json').read_text())['cases'] if c['startup']=='E04_default']
out['limitations'].append('Restored-project playback uses a known factory-pattern descriptor copied into pattern-2 source RAM before normal panel selection; this is a disclosed PC fixture, not playback of the originally restored empty pattern.')
'''
s=s.replace("for case in startup['cases']:",extra+"\nfor case in startup['cases'][1:]:",1)
s=s.replace("   # Change only ordinary root/scale pattern fields; the firmware produces events.","   s.m.uc.mem_write(0x40813531,template)\n   # Known-pattern fixture selected through the guest transition.")
s=s.replace("   s.tap(s.code('PLAY'),hold_ms=100,after_ms=10000)","""   back=rd(s.m.uc,0x4138f214)
   for track in range(4):
    s.m.uc.mem_write(back+track*0x3d0+0x3cb,bytes([61]));s.m.uc.mem_write(back+track*0x3d0+0x3ce,bytes([0 if scenario=='scale' else 255]))
   r['pattern_fixture']={'source_startup':'E04_default','source_backing':hex(template_back),'destination_backing':hex(back),'bytes':len(template),'sha256':hashlib.sha256(template).hexdigest(),'event_fields_injected':False}
   s.tap(s.code('PLAY'),hold_ms=100,after_ms=3000)""")
exec(compile(s,'restored-controlled-pattern-playback','exec'))
