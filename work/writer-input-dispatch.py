exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40014620,0x400146ca),(0x400d7dfe,0x400d7ec0)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-input-dispatch.txt').write_text('\n'.join(out));print('\n'.join(out))
