from pathlib import Path
s=Path('work/test-E08C-running-pattern-handoff.py').read_text()
s=s.replace("s=Session(prepared['checkpoints']['E08C-two-patterns-prepared']", "s=Session('work/os144/E08C-handoff-ready.snap'")
start=s.index("    phase='channel_A01';");end=s.index('    mi=midi.MidiIn();',start)
s=s[:start]+s[end:]
anchor="s=Session('work/os144/E08C-handoff-ready.snap'"
extra=r'''
original_info=info
def info(u):
    kit=rd(u,0x419c5b10);cache=rd(u,0x419c5b14)
    return {**original_info(u),'stock_kit':hex(kit),'stock_M1_cache':hex(cache),
            'effective_M1_data':hex(cache or (kit+0x5ce if kit else 0))}
owner_install=install
def install(s):
    owner_install(s)
    def write(u,access,a,n,value,d):
        event('stock_owner_write',u,address=hex(a),value=hex(value),writer=hex(u.reg_read(UC_M68K_REG_PC)),**info(u))
    s.m.uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x419c5b10,end=0x419c5b23)
    def source(u,pc,n,d):
        p=u.reg_read(UC_M68K_REG_A2)
        if rd(u,p) in [0,1] and rd(u,p+4)==0:
            event('M1_source_owner',u,parameter_pointer=hex(rd(u,p+40)),source_mode=rd(u,p+44),**info(u))
    s.at(0x400f40b4,source)
    def bind(u,pc,n,d):
        sp=u.reg_read(UC_M68K_REG_A7)
        event('parameter_bind',u,parameter_pointer=hex(rd(u,sp+4)),track=rd(u,sp+8),**info(u))
    s.at(0x400f3750,bind)

'''
s=s.replace(anchor,extra+anchor)
s=s.replace('Digitone-E08C-running-pattern-','Digitone-E08D-owner-trace-')
s=s.replace("checkpoint('E08C-after-two-pattern-handoff')","checkpoint('E08D-owner-trace-after-handoff')")
exec(compile(s,'E08D-ownership-trace','exec'))
