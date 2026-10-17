import sys,pathlib,json
sys.path.insert(0,str(pathlib.Path('work/disassembly-deps').resolve()))
from capstone import *
c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
files=[('work/section-2.bin',0x80000400,4),('work/section-3.bin',0x40000400,0)]
out=[]
for f,b,skip in files:
 data=pathlib.Path(f).read_bytes()[skip:]
 for a,n in ([(0x80000e8a,180),(0x80000410,150)] if skip else [(0x400004ec,190)]):
  for i in c.disasm(data[a-b:a-b+n],a):out.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
 for x in [0xfc0c0000,0xfc0c0004,132000000,264000000]:
  needle=x.to_bytes(4,'big');off=0;hits=[]
  while (off:=data.find(needle,off))>=0:hits.append(hex(b+off));off+=1
  out.append(f'{f} literal {x:x} hits {hits}')
pathlib.Path('outputs/Digitone-clock-static-evidence.txt').write_text('\n'.join(out));print('\n'.join(out))
