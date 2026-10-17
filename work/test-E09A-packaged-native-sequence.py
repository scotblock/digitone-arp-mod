"""Native sequence correction installed by the candidate's startup copier."""
from pathlib import Path
import sys
sys.argv=[sys.argv[0],'fixed']
generator=Path('work/test-PC-E09-native-sequence-owner-fix.py').read_text().split("exec(compile(source,'E09-native-sequence-owner-'")[0]
ns={};exec(compile(generator,'packaged-sequence-proof-generator','exec'),ns)
source=ns['source']
source=source.replace("work/test-E09-packaged-panel-playback.py","work/test-E09A-packaged-panel-playback.py")
start=source.index('before_overlay_install=install')
end=source.index("s=Session(case['ui_snapshot']",start)
source=source[:start]+source[end:]
source=source.replace("out['USB_packets']=[];original_install=install", "out['USB_packets']=[];out['owner_fix_host_overlay']=False;original_install=install")
source=source.replace('outputs/Digitone-E09-native-sequence-owner-fixed.json','outputs/Digitone-E09A-packaged-native-sequence.json')
keyboard='''    phase='keyboard_regression'
    send([v for note in [60,64,67] for v in [0x90|channel,note,100]])
    s.run_ms(350)
    phase='keyboard_release'
    send([v for note in [60,64,67] for v in [0x80|channel,note,0]])
    s.run_ms(250);s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
'''
source=source.replace('    def notes(raw):',keyboard+'    def notes(raw):')
needle="    assert din==usb,(din,usb)"
proof='''
    keyboard_notes=notes([b for e in out['wire'] if e['phase']=='keyboard_regression' for b in e['bytes']])
    pitches={n for st,n,v in keyboard_notes if st&0xf0==0x90 and v}
    assert pitches=={60,64,67},('Keyboard arp regression',keyboard_notes)
    out['keyboard_arp_pitches']=sorted(pitches)
    out['keyboard_and_sequence_covered']=True
'''
source=source.replace(needle,needle+'\n'+proof)
exec(compile(source,'E09A-packaged-native-sequence','exec'))
