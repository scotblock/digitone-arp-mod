import sys,struct
from pathlib import Path
sys.path[:0]=['work/disassembly-deps','work/emulator-deps','work/upstream/digiemu']
import capstone
from emu.cfisa import decode
d=Path('work/os144/section-3.bin').read_bytes();base=0x40000400
md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
a=int(sys.argv[1],0);end=int(sys.argv[2],0)
while a<end:
 ins=decode(lambda rel:struct.unpack_from('>H',d,a-base+rel)[0],a)
 raw=d[a-base:a-base+ins.length];dis=next(md.disasm(raw,a,count=1),None)
 print(hex(a),raw.hex(),ins.op,(dis.mnemonic+' '+dis.op_str) if dis else '?','target='+hex(ins.target) if isinstance(ins.target,int) else '')
 a+=ins.length
