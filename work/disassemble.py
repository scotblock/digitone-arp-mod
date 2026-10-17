import sys,pathlib,struct,re
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
b=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400
md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
out=[]
for start,end in [(0x10,0xe8),(0x4eb38,0x4f340),(0xaeaa0,0xaf000),(0x0e8,0x172)]:
 out.append(f'\nWINDOW {start:x}\n')
 for i in md.disasm(b[start:end],base+start):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/disassembly.txt').write_text('\n'.join(out))
print('\n'.join(out[:5]))
print('window lines',len(out))
