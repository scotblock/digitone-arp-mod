from pathlib import Path
s=Path('work/test-E08C-running-pattern-handoff.py').read_text()
s=s.replace("s=Session(prepared['checkpoints']['E08C-two-patterns-prepared']", "s=Session('work/os144/E08C-handoff-ready.snap'")
start=s.index("    phase='channel_A01';")
end=s.index('    mi=midi.MidiIn();',start)
s=s[:start]+s[end:]
anchor="s=Session('work/os144/E08C-handoff-ready.snap'"
control=r'''
original_control_install=install
def install(s):
    global payload
    original_control_install(s)
    spec=json.loads(Path('work/os144/E08C-order-control-layout.json').read_text())
    region=next(r for r in spec['regions'] if r['name']=='observe_M1_binding')
    data=Path('work/os144/E08C-order-control.bin').read_bytes()
    code=data[region['base']-spec['base']:region['base']-spec['base']+region['bytes']]
    from emu import cfisa
    off=0
    while off<len(code):
        ins=cfisa.decode(lambda n:int.from_bytes(code[off+n:off+n+2],'big'),region['base']+off)
        assert ins.length>0 and off+ins.length<=len(code) and not ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF)
        off+=ins.length
    s.m.uc.mem_write(region['base'],code)
    s.m.install_isa_patches_scoped(code,region['base'])
    payload=bytearray(payload)
    offset=region['base']-0x47be0000;payload[offset:offset+len(code)]=code
    for item in layout['regions']:
        if item['name']=='observe_M1_binding':item['bytes']=len(code)
    out['helpers_host_loaded']=True
    out['observer_order_control']=True
    out['control_change']='Suppress automatic UI binding publication while transport is running; native MIDI context and panel paths unchanged.'
    out['canonical_firmware_unchanged']=True

'''
assert anchor in s
s=s.replace(anchor,control+anchor)
s=s.replace('Digitone-E08C-running-pattern-', 'Digitone-E08C-order-control-')
s=s.replace('E08C-handoff-', 'E08C-order-control-')
s=s.replace('work/os144/E08C-order-control-ready.snap','work/os144/E08C-handoff-ready.snap')
s=s.replace("checkpoint('E08C-after-two-pattern-handoff')", "checkpoint('E08C-order-control-after-handoff')")
exec(compile(s,'E08C-handoff-order-control','exec'))
