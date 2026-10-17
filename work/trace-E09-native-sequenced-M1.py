"""Trace a panel-created M1 trig through the real E09 MIDI consumer."""
from pathlib import Path
source = Path('work/test-E09-packaged-M1-both-ports.py').read_text()
source = source.replace("out['USB_packets']=[];original_install=install", "out['USB_packets']=[];original_install=install\nout['native_descriptors']=[];out['dispatch_counts']={}")
marker = "s=Session(case['ui_snapshot']"
pos = source.index(marker)
trace = '''
before_trace_install=install
def install(s):
    before_trace_install(s)
    def observed(u,pc,n,d):
        if phase not in ['native_program','native_play','native_stop']:return
        sp=u.reg_read(UC_M68K_REG_A7)
        ptr=rd(u,sp+4)
        words=[rd(u,ptr+x) for x in range(0,52,4)]
        key=phase+':'+str(words[0])
        out['dispatch_counts'][key]=out['dispatch_counts'].get(key,0)+1
        if words[0] in [0,1,2,4] and sum(e['phase']==phase and e['words'][0]==words[0] for e in out['native_descriptors'])<16:
            root=rd(u,0x419f0de0);ui_data=rd(u,root+0x1008)
            word=lambda a:int.from_bytes(u.mem_read(a+158,2),'big') if a else None
            row={'phase':phase,'ms':s.now_ms(),'pointer':hex(ptr),'words':words,
                 'source_parameter_word':word(words[10]) if words[0] in [0,1] else None,
                 'ui_data':hex(ui_data),'ui_word':word(ui_data),
                 'state':[rd(u,S+x) for x in [4,8,12,16,32,36,336,340]]}
            out['native_descriptors'].append(row)
            print('descriptor',row,flush=True)
    s.m.uc.hook_add(UC_HOOK_CODE,observed,begin=native['entries']['dispatch'],end=native['entries']['dispatch'])
'''
source = source[:pos] + trace + source[pos:]
start = source.index("    send([v for note in [60,64,67]")
end = source.index('    def notes(raw):', start)
source = source[:start] + '''    phase='native_program'
    from emu.snapshot import save
    save(s.m,'work/os144/E09-native-M1-pre-sequence.snap',components={**s.ev['checkpoint_components'],'timers':s.pits},manifest=s.ev.get('checkpoint_manifest'))
    out['native_program_checkpoint']='work/os144/E09-native-M1-pre-sequence.snap'
    s.tap(s.code('SYN1'),hold_ms=100,after_ms=100)
    s.tap(s.code('RECORD'),hold_ms=100,after_ms=100)
    s.tap(s.code('1'),hold_ms=100,after_ms=100)
    s.tap(s.code('RECORD'),hold_ms=100,after_ms=100)
    phase='native_play'
    s.tap(s.code('PLAY'),hold_ms=100,after_ms=100)
    s.run_ms(2500)
    phase='native_stop'
    s.tap(s.code('STOP'),hold_ms=100,after_ms=500)
''' + source[end:]
source = source.replace("    assert din==usb and len(din)>=12,(din,usb)", "    out['observed_DIN_notes']=din;out['observed_USB_notes']=usb\n    assert any(e['phase']=='native_play' and e['words'][0] in [0,1] for e in out['native_descriptors']), 'No sequenced source reached dispatch'\n    assert din==usb,(din,usb)")
source = source.replace('outputs/Digitone-E09-packaged-M1-both-ports.json', 'outputs/Digitone-E09-native-sequenced-M1-trace.json')
exec(compile(source, 'E09-native-sequenced-M1-trace', 'exec'))
