exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40034d46,0x40034dcc),(0x40035340,0x40035438),(0x400134e4,0x40013564),(0x400dae08,0x400dae6a),(0x4012c344,0x4012c3e2)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/writer-exit-ends-and-allocation.txt').write_text('\n'.join(out));print('\n'.join(out))
