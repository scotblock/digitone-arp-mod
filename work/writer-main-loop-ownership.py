exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for off in range(0,0x170000-6,2):
 op=struct.unpack_from('>H',b,off)[0]
 if op in (0x6100,0x6000,0x4eba,0x4efa) and base+off+2+struct.unpack_from('>h',b,off+2)[0]==0x40016d56:out.append(f'PCREF {base+off:08x}')
for s,e in [(0x400171e2,0x40017214),(0x40131054,0x401310ac),(0x40130c4e,0x40130c74)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-main-loop-ownership.txt').write_text('\n'.join(out));print('\n'.join(out))
