exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for off in range(0,0xb0,4):out.append(f'TABLE {0x401a4958+off:08x} +{off:02x}: {struct.unpack_from(">I",b,0x401a4958-base+off)[0]:08x}')
for s,e in [(0x400b6b16,0x400b6cb2),(0x400eeafa,0x400eeb10),(0x40015b9a,0x40015be0),(0x4013b2d4,0x4013b310)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-ui-vtable.txt').write_text('\n'.join(out));print('\n'.join(out))
