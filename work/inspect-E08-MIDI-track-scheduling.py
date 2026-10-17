from pathlib import Path
import sys
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
b=Path('work/os144/E07-PC-main.bin').read_bytes();base=0x40000400;m=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
lines=[]
for a,z in [(0x400eabb4,0x400eaf50),(0x400edbc2,0x400ede80),(0x400f3c1a,0x400f3d90),(0x40097d00,0x40098116),(0x400f0578,0x400f062e)]:
 lines.append('WINDOW '+hex(a));lines += [f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}' for i in m.disasm(b[a-base:z-base],a)]
Path('work/E08-MIDI-track-scheduling-disassembly.txt').write_text('\n'.join(lines))
print('\n'.join(lines[:110]))
