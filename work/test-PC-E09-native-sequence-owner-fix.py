"""Current/fixed controls from the same packaged E09 startup state."""
from pathlib import Path
import sys
label=sys.argv[1] if len(sys.argv)>1 else 'fixed'
assert label in ['current','fixed']
generator=Path('work/trace-E09-native-sequenced-M1.py').read_text().split("exec(compile(source, 'E09-native-sequenced-M1-trace'")[0]
ns={};exec(compile(generator,'native-sequence-trace-generator','exec'),ns)
source=ns['source']
# Retain the native prepared UI/settings/transport state, not synthetic notes.
source=source.replace("assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]", "assert rd(s.m.uc,S)==0x4d314131")
source=source.replace("exec(compile(prefix,", "prefix=prefix.replace('assert [rd(s.m.uc,S+x) for x in [0,4,304,308]] == [0x4d314131,0,2,50]', 'assert rd(s.m.uc,S)==0x4d314131')\nexec(compile(prefix,")
setup='''    # RATE is changed through the native M1 menu, making the default short
    # trig long enough for multiple 1/96 arp pulses instead of one raw note.
    s.press(s.code('FUNC'));s.run_ms(100)
    s.tap(s.code('SYN2'),hold_ms=100,after_ms=150)
    s.release(s.code('FUNC'));s.run_ms(150)
    for _ in range(3):s.turn(2,16,after_ms=120)
    s.tap(s.code('NO'),hold_ms=100,after_ms=150)
    assert rd(s.m.uc,S+4)==1 and rd(s.m.uc,S+304)==5, [rd(s.m.uc,S+x) for x in [4,304,308,320]]
    out['arp_rate_set_through_native_UI']='1/96'
    for a,v in [(0x419c5df4,3),(0x40529244,1),(0xfc0b01c4,1),(0x40529248,0),(0x4052924c,0),(0x40529234,0)]:s.m.uc.mem_write(a,struct.pack('>I',v))
    out['wire']=[];out['USB_packets']=[]
'''
source=source.replace("    phase='native_program'",setup+"    phase='native_program'",1)
# Do not replace the common checkpoint when running the controls.
start=source.index('    from emu.snapshot import save')
end=source.index("    s.tap(s.code('SYN1')",start)
source=source[:start]+source[end:]
pos=source.index("s=Session(case['ui_snapshot']")
overlay='''
before_overlay_install=install
def install(s):
    global payload
    before_overlay_install(s)
    out['owner_fix_host_overlay']=OVERLAY
    if OVERLAY:
        out['helpers_host_loaded']=True
        cfg=json.loads(Path('work/os144/PC_ONLY-E09-sequence-owner-helper.json').read_text())
        code=Path('work/os144/PC_ONLY-E09-sequence-owner-helper.bin').read_bytes()
        address=cfg['region']['base']
        old=bytes(s.m.uc.mem_read(address,len(code)))
        assert hashlib.sha256(old).hexdigest()==cfg['before_sha256']
        s.m.uc.mem_write(address,code);s.m.install_isa_patches_scoped(code,address)
        payload=bytearray(payload);payload[address-native['base']:address-native['base']+len(code)]=code
'''.replace('OVERLAY',repr(label=='fixed'))
source=source[:pos]+overlay+source[pos:]
needle="    assert din==usb,(din,usb)"
proof='''
    sequence=[e for e in out['native_descriptors'] if e['phase']=='native_play' and e['words'][0]==0]
    assert sequence,'No actual sequenced note witness'
    beginning=sequence[0]['ms']
    pulses=[]
    for event in out['wire']:
        if event['phase']=='native_play' and event['ms']>=beginning:
            for message in notes(event['bytes']):
                if message[0]&0xf0==0x90 and message[2]:pulses.append({'ms':event['ms'],'note':message[1]})
    out['sequenced_arp_pulses']=pulses
    out['sequenced_pulse_count']=len(pulses)
    if FIXED:
        assert len(pulses)>=3,('No repeated sequenced arp pulses',pulses)
        assert all(e['state'][0]==1 for e in sequence),'Arp disabled on sequenced owner selection'
    else:
        assert len(pulses)==1,pulses
        assert all(e['state'][0]==0 for e in sequence),'Current-build regression not reproduced'
'''.replace('FIXED',repr(label=='fixed'))
source=source.replace(needle,needle+'\n'+proof)
source=source.replace('outputs/Digitone-E09-native-sequenced-M1-trace.json',f'outputs/Digitone-E09-native-sequence-owner-{label}.json')
exec(compile(source,'E09-native-sequence-owner-'+label,'exec'))
