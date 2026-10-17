from pathlib import Path
import sys,struct,re
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
b=Path('work/os144/E07-PC-main.bin').read_bytes();base=0x40000400;m=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE);lines=[]
for target in [0x80004614,0x401ac618,2700000,5400000]:
 lines.append('TARGET '+hex(target))
 hits=[base+x.start() for x in re.finditer(re.escape(struct.pack('>I',target)),b)]
 lines += ['REF '+hex(x) for x in hits]
 for hit in hits[:24]:
  # Aligned exact instruction start commonly precedes a 32-bit operand by 2.
  a=hit-2;z=hit+44
  lines.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}' for i in m.disasm(b[a-base:z-base],a))
for a,z in [(0x40096690,0x40096940),(0x4029c4b0,0x4029c51e)]:
 lines.append('WINDOW '+hex(a));lines.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}' for i in m.disasm(b[a-base:z-base],a))
Path('work/E08-tempo-and-copier-disassembly.txt').write_text('\n'.join(lines));print('\n'.join(lines[:80]));print('\n'.join(lines[-40:]))
