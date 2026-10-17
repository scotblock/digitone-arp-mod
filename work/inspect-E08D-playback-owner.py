from pathlib import Path
import sys,struct,re
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
data=Path('work/os144/E08C-PC-layout-main.bin').read_bytes();base=0x40000400
md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
lines=[]
for start,end in [(0x400f3750,0x400f37ce),(0x400f40ba,0x400f4126),(0x400f4300,0x400f4450)]:
    lines.append('WINDOW '+hex(start))
    lines.extend(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:10} {i.op_str}' for i in md.disasm(data[start-base:end-base],start))
for target in [0x419c5b10,0x419c5b14]:
    lines.append('ABSOLUTE REFERENCES '+hex(target))
    for match in re.finditer(re.escape(struct.pack('>I',target)),data[:0x19f000]):
        at=base+match.start();lines.append(hex(at))
        start=max(base,at-8)
        lines.extend(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:10} {i.op_str}' for i in md.disasm(data[start-base:at-base+16],start))
Path('work/E08D-playback-owner.txt').write_text('\n'.join(lines))
print('\n'.join(lines[:135]))
