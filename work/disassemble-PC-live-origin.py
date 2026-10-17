from pathlib import Path
exec(Path('work/audit-E04-startup-ISA.py').read_text().split('\nregions=')[0])
from capstone import Cs,CS_ARCH_M68K,CS_MODE_M68K_040,CS_MODE_BIG_ENDIAN
b=Path('work/os144/section-3.bin').read_bytes();base=0x40000400
md=Cs(CS_ARCH_M68K,CS_MODE_M68K_040|CS_MODE_BIG_ENDIAN)
lines=[]
for start,end in [(0x400ff3e8,0x400ff61a),(0x4009e640,0x4009e668),(0x40100252,0x401002b6)]:
 p=start;lines.append('\n'+hex(start))
 while p<end:
  ins=cfisa.decode(lambda off:int.from_bytes(b[p-base+off:p-base+off+2],'big'),p)
  raw=b[p-base:p-base+ins.length];pretty=' '.join(x.mnemonic+' '+x.op_str for x in md.disasm(raw,p))
  lines.append(f'{p:08x} {raw.hex():16} {ins.op:8} {pretty}');p+=ins.length
Path('work/PC-live-origin-disassembly.txt').write_text('\n'.join(lines));print('\n'.join(lines))
