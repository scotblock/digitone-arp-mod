exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40034174,0x400342c0),(0x40031d2a,0x40031d90),(0x40032550,0x400325d8)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-track-storage.txt').write_text('\n'.join(out));print('\n'.join(out))
