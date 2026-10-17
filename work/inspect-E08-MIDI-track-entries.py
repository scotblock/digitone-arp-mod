from pathlib import Path
import sys,struct,re
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
b=Path('work/os144/E07-PC-main.bin').read_bytes();base=0x40000400
m=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
windows=[(0x400f0416,0x400f0690),(0x400250a4,0x40025400),(0x40025e66,0x40026140),(0x4009755e,0x40097848),(0x400f3c1a,0x400f4062)]
lines=[]
for a,z in windows:
 lines.append('WINDOW '+hex(a))
 lines.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}' for i in m.disasm(b[a-base:z-base],a))
for target in [0x400f0416,0x400250a4,0x40025e66,0x4009755e,0x400f3c1a]:
 lines.append('REFERENCES '+hex(target))
 for hit in re.finditer(re.escape(struct.pack('>I',target)),b):lines.append('ABS '+hex(base+hit.start()))
 for off in range(0,min(len(b)-4,0x170000),2):
  if b[off:off+2] in [b'\x4e\xba',b'\x61\x00'] and base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:lines.append('PC '+hex(base+off))
Path('work/E08-MIDI-track-entry-disassembly.txt').write_text('\n'.join(lines))
print('\n'.join(lines[:100]));print('\n'.join(lines[-35:]))
