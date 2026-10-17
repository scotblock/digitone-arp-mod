import pathlib,sys
sys.path.insert(0,str(pathlib.Path('work/disassembly-deps').resolve()))
from capstone import *
c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
out=[]
for f,base,skip,ranges in [('work/section-3.bin',0x40000400,0,[(0x4000051e,30),(0x40000f66,590)]),('work/section-2.bin',0x80000400,4,[(0x80004ece,530)])]:
 data=pathlib.Path(f).read_bytes()[skip:];out.append(f)
 for a,n in ranges:
  for i in c.disasm(data[a-base:a-base+n],a):out.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
pathlib.Path('outputs/Digitone-SSI1-clock-aligned-disassembly.txt').write_text('\n'.join(out));print('\n'.join(out[:100]))
