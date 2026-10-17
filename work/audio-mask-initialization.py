exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40001ee0,0x40001f70),(0x4000232c,0x400023b6),(0x4009c8cc,0x4009c934)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/audio-mask-initialization.txt').write_text('\n'.join(out));print('\n'.join(out))
