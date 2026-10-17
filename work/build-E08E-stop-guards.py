"""Separate native Stop/disable correction; E08D package is preserved."""
from pathlib import Path
s=Path('work/build-E08D-owner-guards.py').read_text().replace('E08D','E08E')
needle="absop(a,'23c0',S+4)\na.label('clear')"
assert needle in s
s=s.replace(needle,"absop(a,'23c0',S+4);a.emit('4a80');a.branch('6600','mode_ready');js(a,0x47be7400);a.label('mode_ready')\n\na.label('clear')")
extra=r"""
helpers+=r'''
# Quiesce M1 generation, retaining a busy arena until its actual retirement.
a=Asm();save(a);absop(a,'2039',S);a.emit('0c804d314131');a.branch('6600','end');absop(a,'2039',0x47be2840);a.emit('0c804c495645');a.branch('6600','end')
for off in [8,12]:absop(a,'42b9',S+off)
js(a,native['entries']['clear']);a.label('end');done_void(a);add('M1_quiesce_generation',0x47be7400,a,128)
# Stock task command 4 handles Stop outside the descriptor consumer. Join it
# before stock drains its outgoing note lists, then replay the exact MOVEA.
a=Asm();js(a,0x47be7400);a.emit(main[0x400f4aec-0x40000400:0x400f4af2-0x40000400].hex());jmp(a,0x400f4af2);add('M1_stock_stop_bridge',0x47be7480,a,128);hook(0x400f4aec,0x47be7480,6)
'''
"""
anchor='marker="Path('
at=s.index(anchor);s=s[:at]+extra+'\n'+s[at:]
exec(compile(s,'E08E-stop-guard-builder','exec'))
