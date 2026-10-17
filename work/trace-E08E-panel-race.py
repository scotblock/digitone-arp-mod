"""Observe complete panel admission around a native pattern handoff."""
from pathlib import Path
source=Path('work/test-E08E-live-edit-handoff.py').read_text()
source=source.replace('Digitone-E08E-live-edit','Digitone-E08E-panel-race-trace')
source=source.replace("snapshot_mark('A02_requested')", "snapshot_mark('A02_requested');checkpoint('E08E-panel-race-requested')")
source=source.replace("for pc in [0x47be5f00,0x47be6300]:s.at(pc,panel_probe)",r'''
from unicorn.m68k_const import UC_M68K_REG_D2,UC_M68K_REG_A4,UC_M68K_REG_A0
def detailed(u,pc,n,d):
    sp=u.reg_read(UC_M68K_REG_A7)
    row=dict(handler=hex(pc),a4=hex(u.reg_read(UC_M68K_REG_A4)),d2=hex(u.reg_read(UC_M68K_REG_D2)),
        args=[hex(rd(u,sp+i*4)) for i in range(4)])
    if pc in [0x47be6300,0x47be6500,0x47be6000]:
        view=rd(u,sp+4);row['view']=hex(view);row['view_tag']=hex(rd(u,view+0x2c8))
    event('detailed_panel',u,**row,**info(u))
for pc in [0x47be5f00,0x47be6300,0x47be6500,0x47be6c80,0x47be6600,0x4003fc42,0x4003fc60,0x47be7000]:s.at(pc,detailed)
''')
exec(compile(source,'E08E-panel-race-trace','exec'))
