exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4009ca40,0x4009cb10),(0x4009c88a,0x4009c8da)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/audio-queue-entry-gates.txt').write_text('\n'.join(out));print('\n'.join(out))
