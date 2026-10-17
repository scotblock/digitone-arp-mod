import pathlib,sys
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu import snapshot
p=next(pathlib.Path('work/continuous-emulator/snapshots').rglob('gui.snap'));b=snapshot._load_blob(str(p))
print('page type',type(b['pages']).__name__)
print('keys',list(b.keys())[:10])
