from pathlib import Path
import sys,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
import capstone
from emu.cfisa import decode
p=Path(sys.argv[1]);base=int(sys.argv[2],0);a=int(sys.argv[3],0);end=int(sys.argv[4],0);data=p.read_bytes();md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
while a<end:
 ins=decode(lambda r:struct.unpack_from('>H',data,a-base+r)[0],a);raw=data[a-base:a-base+ins.length];dis=next(md.disasm(raw,a,count=1),None)
 print(hex(a),raw.hex(),ins.op,(dis.mnemonic+' '+dis.op_str) if dis else '?');a+=ins.length
