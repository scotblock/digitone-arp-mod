exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400ef810,0x400efa50),(0x400ee696,0x400ee7b0),(0x4009c2f8,0x4009c350),(0x4009727e,0x40097370)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/live-held-note-state.txt').write_text('\n'.join(lines));print('\n'.join(lines))
