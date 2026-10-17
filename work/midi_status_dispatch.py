exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400dfc1a,0x400dfe1a)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/midi-status-dispatch.txt').write_text('\n'.join(lines));print('\n'.join(lines))
