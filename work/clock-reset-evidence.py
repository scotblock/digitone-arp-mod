import pathlib,sys,json
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from dt2.container import sections
from emu import snapshot
p=r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'
c,secs=sections(p)
print('sections',secs)
print('header',c[:100].hex())
snap=next(pathlib.Path('work/continuous-emulator/snapshots').rglob('gui.snap'))
b=snapshot._load_blob(str(snap))
print('control', {hex(k):hex(v) for k,v in b['ctlregs'].items()})

