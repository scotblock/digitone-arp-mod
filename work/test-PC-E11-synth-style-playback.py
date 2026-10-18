"""E11 UI controls plus native keyboard/sequence playback on PC overlays."""
from pathlib import Path
s=Path('work/test-PC-E10-package-playback.py').read_text(encoding='utf-8')
s=s.replace('outputs/Digitone-E10-PC-package-playback.json','outputs/Digitone-E11-PC-synth-style-playback.json')
anchor="exec(compile(source,'E10-packaged-native-editor-playback','exec'))"
extra='''
inner="exec(compile(source,'E10-copied-native-editor-and-playback','exec'))"
inject="""
position=source.index("s=Session(case['ui_snapshot']")
overlay=\\"\\"\\"
previous_install=install

def install(s):
    global payload
    previous_install(s)
    payload=bytearray(payload)
    config=json.loads(Path('work/os144/PC_ONLY-E11-synth-style-editor.json').read_text())
    data=Path('work/os144/PC_ONLY-E11-synth-style-editor.bin').read_bytes()
    for page in range(config['base'],config['base']+len(data),4096):s.m.ensure(page)
    s.m.uc.mem_write(config['base'],data)
    for r in config['regions']:
        piece=data[r['base']-config['base']:r['base']-config['base']+r['bytes']]
        s.m.install_isa_patches_scoped(piece,r['base'])
    for patch in config['patches']:
        assert bytes(s.m.uc.mem_read(patch['site'],6)).hex()==patch['before']
        code=bytes.fromhex(patch['after']);s.m.uc.mem_write(patch['site'],code)
        off=patch['site']-native['base'];payload[off:off+6]=code
    out.update(helpers_host_loaded=True,hooks_host_patched=True,E11_PC_overlay=True)
\\"\\"\\"
source=source[:position]+overlay+source[position:]
source=source.replace('for _ in range(12):s.turn(3,-16,after_ms=100)','for _ in range(12):s.turn(6,-16,after_ms=100)')
source=source.replace('s.turn(5,16,after_ms=100)',"s.tap(s.code('RIGHT'),hold_ms=80,after_ms=100)")
source=source.replace('for _ in range(step):s.turn(6,16,after_ms=100)','for _ in range(step):s.turn(5,16,after_ms=100)')
source=source.replace('if step==2:s.turn(7,16,after_ms=100)',"if step==2:s.tap(s.code('DOWN'),hold_ms=80,after_ms=100)")
source=source.replace('for _ in range(3):s.turn(5,-16,after_ms=100)',"for _ in range(3):s.tap(s.code('LEFT'),hold_ms=80,after_ms=100)")
source=source.replace('outputs/Digitone-E10-PC-package-playback.json','outputs/Digitone-E11-PC-synth-style-playback.json')
"""
assert inner in source;source=source.replace(inner,inject+'\\n'+inner)
'''
assert anchor in s;s=s.replace(anchor,extra+'\n'+anchor)
exec(compile(s,'E11-native-control-playback-driver','exec'))
import json
p=Path('outputs/Digitone-E11-PC-synth-style-playback.json');r=json.loads(p.read_text());assert r['passed']
r.update(E11_PC_overlay=True,helpers_host_loaded=True,hooks_host_patched=True,firmware_container_created=False,internal_loader_test_only=False,firmware_release_created=False,hardware_ready=False)
r['limits']=['Native packaged E10 base, with explicit PC-installed E11 UI code and three handler patches. No E11 startup/container or hardware claim.','Actual arrow/E/F panel programming then native keyboard/sequencer playback and matching DIN/USB fixture output. No settings/bank values are host-written.','Inherited MIDI gate/routing/USB endpoint and timing/peripheral fixtures remain. E10 firmware is unchanged.']
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
