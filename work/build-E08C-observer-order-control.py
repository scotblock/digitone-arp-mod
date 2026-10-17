"""Isolated PC experiment; canonical builders/package files remain unchanged."""
from pathlib import Path
s=Path('work/build-E08-M1-controls-overlay.py').read_text()
needle="absop(a,'2079',0x419f0de0);a.emit('4a88')"
assert s.count(needle)==1
guard="absop(a,'2079',S+40);a.emit('4a88');a.branch('6700','end');a.emit('20100c8000000001');a.branch('6700','end');"
s=s.replace(needle,guard+needle)
s=s.replace('E08-PC-M1-controls.bin','E08C-order-control.bin').replace('E08-PC-M1-controls-layout.json','E08C-order-control-layout.json')
exec(compile(s,'E08C-observer-order-control-builder','exec'))
