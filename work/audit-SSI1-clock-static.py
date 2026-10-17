import sys,pathlib
sys.path.insert(0,str(pathlib.Path('work/disassembly-deps').resolve()))
from capstone import *
c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE);out=[]
for f,b,skip in [('work/section-2.bin',0x80000400,4),('work/section-3.bin',0x40000400,0)]:
 d=pathlib.Path(f).read_bytes()[skip:]
 for x in (0xec09000e,0xec090010):
  pos=0
  while (pos:=d.find(x.to_bytes(4,'big'),pos))>=0:
   out.append(f'{f} literal {x:x} at {b+pos:08x}')
   for i in c.disasm(d[max(0,pos-20):pos+50],b+max(0,pos-20)):out.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
   pos+=1
pathlib.Path('outputs/Digitone-SSI1-clock-static.txt').write_text('\n'.join(out));print('\n'.join(out))
