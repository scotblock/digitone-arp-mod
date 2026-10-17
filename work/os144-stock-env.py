import sys,os,hashlib,struct
from pathlib import Path
sys.path[:0]=[str(Path('work/emulator-deps').resolve()),str(Path('work/upstream/digiemu').resolve())]
from emu import bootstrap as bs
SYX=Path('inputs/Digitone_and_Digitone_Keys_OS1.44.syx')
assert hashlib.sha256(SYX.read_bytes()).hexdigest()=='d4f200d04484333d82822db7744e6484d0def8f2db8ddf55ee2b780cc13c9659'
ROOT=Path('work/os144-stock-engine').resolve();ROOT.mkdir(exist_ok=True)
class Paths(bs.FirmwarePaths):
 @property
 def syx(self):return str(SYX)
paths=Paths(str(ROOT),SYX.name,str(Path('work/upstream/digiemu/devices').resolve()))
os.environ.update(paths.env())
DDR=0x08000000
def rd(uc,a):return struct.unpack('>I',uc.mem_read(a,4))[0]
def u32(x):return struct.pack('>I',x&0xffffffff)
