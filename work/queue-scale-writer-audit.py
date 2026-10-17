exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x40032550,0x4003267c),(0x40032816,0x400328a8)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/queue-scale-writer-audit.txt').write_text('\n'.join(lines));print('\n'.join(lines))
