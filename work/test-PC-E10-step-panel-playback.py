"""Native panel creates a four-step scale-degree/rest sequence, then plays it."""
from pathlib import Path
generator=Path('work/test-PC-E10-step-playback.py').read_text().split("exec(compile(source,'E10-PC-step-playback'")[0]
ns={};exec(compile(generator,'E10-panel-playback-generator','exec'),ns)
source=ns['source']
pos=source.index("s=Session(case['ui_snapshot']")
install='''
before_editor_install=install
def install(s):
    global payload
    before_editor_install(s)
    for stem in ['publication','editor']:
        config=json.loads(Path('work/os144/PC_ONLY-E10-step-'+stem+'.json').read_text())
        data=Path('work/os144/PC_ONLY-E10-step-'+stem+'.bin').read_bytes()
        for page in range(config['base'],config['base']+len(data),4096):s.m.ensure(page)
        s.m.uc.mem_write(config['base'],data)
        if 'regions' in config:
            for r in config['regions']:
                offset=r['base']-config['base'];s.m.install_isa_patches_scoped(data[offset:offset+r['bytes']],r['base'])
        else:s.m.install_isa_patches_scoped(data,config['base'])
        for patch in config.get('patches',[]):
            address=patch['site'];replacement=bytes.fromhex(patch['after'])
            assert bytes(s.m.uc.mem_read(address,6)).hex()==patch['before']
            s.m.uc.mem_write(address,replacement);offset=address-native['base'];payload[offset:offset+6]=replacement
'''
source=source[:pos]+install+source[pos:]
start=source.index("    cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text())",source.index('try:'))
end=source.index("    phase='native_program'",start)
setup='''    cfg=json.loads(Path('work/os144/PC_ONLY-E10-step-engine.json').read_text());extra=cfg['state']
    phase='native_editor'
    s.tap(s.code('SYN1'),hold_ms=100,after_ms=100)
    s.press(s.code('FUNC'));s.run_ms(100);s.tap(s.code('SYN2'),hold_ms=100,after_ms=150)
    s.release(s.code('FUNC'));s.run_ms(150)
    s.turn(4,16,after_ms=150)
    assert rd(s.m.uc,extra+56)==1 and rd(s.m.uc,extra+28)!=0,'Step page did not open/bind'
    for encoder in [1,2]:
        s.turn(encoder,16,after_ms=100);s.turn(encoder,-16,after_ms=100)
    for _ in range(12):s.turn(3,-16,after_ms=100)
    assert rd(s.m.uc,extra+8)==4
    for step in range(1,4):
        s.turn(5,16,after_ms=100)
        for _ in range(step):s.turn(6,16,after_ms=100)
        if step==2:s.turn(7,16,after_ms=100)
    for _ in range(3):s.turn(5,-16,after_ms=100)
    s.turn(8,16,after_ms=200)
    assert [rd(s.m.uc,extra+x) for x in [4,8,16,20,24]]==[1,4,0,0xfffb,0x80000080]
    assert bytes(s.m.uc.mem_read(extra+32,4))==bytes([0,1,2,3])
    if s.frames:panel.write_png(s.frames[-1][1],'outputs/E10-PC-native-step-editor.png',4)
    out.update(step_config_is_fixture=False,state_initialization_is_fixture=True,native_panel_editor_used=True,
               native_step_program={'offsets':[0,1,2,3],'length':4,'rests_zero_based':[2],'root':'C','scale':'Ionian'})
    s.turn(4,-16,after_ms=150);assert rd(s.m.uc,extra+56)==0
    s.tap(s.code('NO'),hold_ms=100,after_ms=150)
'''
source=source[:start]+setup+source[end:]
source=source.replace('pitches=={60,62,65,67,71,72}','pitches=={60,62,65}')
source=source.replace('outputs/Digitone-E10-PC-step-playback.json','outputs/Digitone-E10-PC-step-panel-playback.json')
exec(compile(source,'E10-native-step-panel-playback','exec'))
