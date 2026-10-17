exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400d6960,0x400d6a02),(0x400d6720,0x400d680a),(0x400b5bc8,0x400b5c7c),(0x4013b25c,0x4013b2d4)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-outer-update.txt').write_text('\n'.join(out));print('\n'.join(out))
