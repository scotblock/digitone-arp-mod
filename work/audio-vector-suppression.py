exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400eef20,0x400eefb0),(0x4008d9c0,0x4008d9f2),(0x4008dce0,0x4008dd04),(0x400d921c,0x400d9274),(0x4008ce9c,0x4008ced6)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/audio-vector-suppression.txt').write_text('\n'.join(out));print('\n'.join(out))
