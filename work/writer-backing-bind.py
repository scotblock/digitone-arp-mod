exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4001fc74,0x4001ff00),(0x40022432,0x40022690),(0x4013a344,0x4013a42e)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-backing-bind.txt').write_text('\n'.join(out));print('\n'.join(out[:240]))
