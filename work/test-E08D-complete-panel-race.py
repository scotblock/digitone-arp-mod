"""Real UART panel edit, save notification and owner rejection at handoff."""
from pathlib import Path
source=Path('work/trace-E08D-panel-race.py').read_text()
# Expand the trace driver without executing it so the original PC-only
# comparison and its evidence remain intact.
prefix=source[:source.index("exec(compile(source,'E08D-panel-race-trace'")]
scope={};exec(compile(prefix,'expand-panel-trace','exec'),scope)
source=scope['source']
source=source.replace('Digitone-E08D-panel-race-trace','Digitone-E08D-complete-panel-race')
source=source.replace("phase='await_incoming_UI';s.press(s.code('FUNC'))", "phase='await_incoming_UI'")
start=source.index("    # Native pattern rebinding closes the page.")
end=source.index("    after=snapshot_mark('incoming_edit_deferred')",start)
source=source[:start]+"    phase='edit_incoming_before_context';s.turn(3,16,after_ms=80)\n"+source[end:]
source=source.replace("    reached=word(s.m.uc)==0xacb2", "    reached=word(s.m.uc)==0xacb2\n    assert reached, 'The actual incoming panel edit must reach the native record in this test'")
# Add observations to the real write/dirty/publisher calls and their native
# returns. No code, settings, admission state or PC is replaced by these hooks.
anchor="def snapshot_mark(label):"
extra=r'''
from unicorn.m68k_const import UC_M68K_REG_D0
returns={}
def boundary(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7);ret=rd(u,sp)
    count={0x47be5900:4,0x4014eff8:2,0x47be7000:3}[pc]
    args=[rd(u,sp+4+i*4) for i in range(count)]
    event('panel_boundary_enter',u,callee=hex(pc),args=[hex(v) for v in args],return_pc=hex(ret),**info(u))
    returns.setdefault(ret,[]).append((pc,args))
    if len(returns[ret])==1 and ret not in hooked:
        hooked.add(ret);s.at(ret,boundary_return)
def boundary_return(u,pc,n,d):
    frames=returns.get(pc)
    if not frames:return
    callee,args=frames.pop()
    event('panel_boundary_return',u,callee=hex(callee),args=[hex(v) for v in args],result=hex(u.reg_read(UC_M68K_REG_D0)),**info(u))
hooked=set()
for pc in [0x47be5900,0x4014eff8,0x47be7000]:s.at(pc,boundary)
'''
source=source.replace(anchor,extra+'\n'+anchor)
Path('work/generated-E08D-complete-panel-race.py').write_text(source)
exec(compile(source,'E08D-complete-panel-race','exec'))
