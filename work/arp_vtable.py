import sys,pathlib,struct,json,re
sys.path.insert(0,'work/disassembly-deps')
from capstone import *
b=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400
md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_COLDFIRE)
u=lambda off:struct.unpack_from('>I',b,off)[0]
lines=[];entries=[]
def emit(s):lines.append(s)
def refs(addr):
 needle=struct.pack('>I',addr)
 return [m.start() for m in re.finditer(re.escape(needle),b)]
for off in range(0x1798e0,0x179a00,4):
 v=u(off);emit(f'TABLE {base+off:08x} {v:08x}')
 if 0x179934<=off<0x179980:
  entries.append({'slot':(off-0x179934)//4,'table_address':hex(base+off),'target':hex(v)})
targets=sorted(set([int(e['target'],16) for e in entries if base<=int(e['target'],16)<base+0x170000]+[0x4004e428,0x4004e448,0x4002ecea,0x4002ee82,0x4002ef20,0x4002fd8e]))
for addr in targets:
 off=addr-base;emit(f'\nFUNCTION {addr:08x} refs {[hex(base+x) for x in refs(addr)][:30]}')
 for i in md.disasm(b[off:off+320],addr):
  emit(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
  if i.mnemonic=='rts' or (i.mnemonic=='jmp' and '(pc' not in i.op_str):break
for addr in [0x401b7f83,0x40179cd0,0x40179cb0]:
 off=addr-base;end=b.find(b'\0',off);emit(f'STRING {addr:08x} {b[off:end]!r}')
pathlib.Path('work/arp-vtable.txt').write_text('\n'.join(lines))
pathlib.Path('work/arp-vtable.json').write_text(json.dumps(entries,indent=2))
print('\n'.join(lines))
