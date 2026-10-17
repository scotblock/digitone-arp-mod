import pathlib,sys,json,struct
sys.path.insert(0,str(pathlib.Path('work/disassembly-deps').resolve()))
from capstone import *
c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE);c.skipdata=True
raw=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400
text=[]
for a,n in [(0x400028cc,80),(0x40002cd2,60),(0x4008c576,44),(0x40002044,80)]:
 for i in c.disasm(raw[a-base:a-base+n],a):text.append(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
p=pathlib.Path('outputs/Digitone-clock-static-evidence.txt');p.write_text(p.read_text()+'\n\n'+'\n'.join(text));print('\n'.join(text))
