exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400ec23c,0x400ec282),(0x400ec284,0x400ec2e0),(0x4000879c,0x4000882e),(0x40013370,0x4001341c)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/writer-data-only-scopes.txt').write_text('\n'.join(out));print('\n'.join(out))
