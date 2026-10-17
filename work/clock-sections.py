import pathlib,sys,struct,json
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu.bootrom import container_section
p=r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'
for sid in [1,2,4]:
 s=container_section(p,sid);print(sid,len(s) if s else None,s[:60].hex() if s else None)
 if sid==1 and s:pathlib.Path('work/section-1-clock.bin').write_bytes(s)
