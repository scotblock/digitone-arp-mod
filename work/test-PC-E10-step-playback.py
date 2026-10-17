"""Continuous native E09A input/sequence + PC-only machine-code step overlay."""
from pathlib import Path
generator=Path('work/test-E09A-packaged-native-sequence.py').read_text().split("exec(compile(source,'E09A-packaged-native-sequence'")[0]
ns={};exec(compile(generator,'E10-step-playback-generator','exec'),ns)
source=ns['source']
position=source.index("s=Session(case['ui_snapshot']")
overlay='''
before_step_install=install
def install(s):
    global payload
    before_step_install(s)
    cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())
    blob=Path('work/os144/PC_ONLY-E10-step-engine.bin').read_bytes()
    for page in range(cfg['base'],cfg['base']+len(blob),4096):s.m.ensure(page)
    s.m.uc.mem_write(cfg['base'],blob)
    payload=bytearray(payload)
    for patch in cfg['patches']:
        address=patch['site'];new=bytes.fromhex(patch['after'])
        assert bytes(s.m.uc.mem_read(address,6)).hex()==patch['before']
        s.m.uc.mem_write(address,new);offset=address-native['base'];payload[offset:offset+6]=new
    for r in cfg['regions']:
        offset=r['base']-cfg['base'];s.m.install_isa_patches_scoped(blob[offset:offset+r['bytes']],r['base'])
    out.update(helpers_host_loaded=True,step_engine_host_overlay=True,step_config_is_fixture=True,
               firmware_container_created=False,prototype_settings_saved_to_project=False)
'''
source=source[:position]+overlay+source[position:]
setup='''    cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())
    extra=cfg['state'];data=rd(s.m.uc,rd(s.m.uc,0x419f0de0)+0x1008)
    for offset,value in [(4,1),(8,8),(20,0xdb),(24,0x80000080),(28,data)]:s.m.uc.mem_write(extra+offset,struct.pack('>I',value))
    s.m.uc.mem_write(extra+32,bytes(range(8)))
    out['step_fixture']={'offsets':list(range(8)),'rests_zero_based':[2,5],'length':8,'root':'C','scale':'Ionian','owner':hex(data)}
'''
source=source.replace("    phase='native_program'",setup+"    phase='native_program'",1)
source=source.replace('for note in [60,64,67]','for note in [60]')
source=source.replace('pitches=={60,64,67}','pitches=={60,62,65,67,71,72}')
source=source.replace("    out['keyboard_and_sequence_covered']=True", "    out['keyboard_and_sequence_covered']=True\n    out['native_step_state']={str(x):rd(s.m.uc,extra+x) for x in [4,8,12,48,52,60]}\n    assert rd(s.m.uc,extra+48)>0 and rd(s.m.uc,extra+12)==0, 'Rest or stop cursor handling failed'")
source=source.replace('outputs/Digitone-E09A-packaged-native-sequence.json','outputs/Digitone-E10-PC-step-playback.json')
exec(compile(source,'E10-PC-step-playback','exec'))
