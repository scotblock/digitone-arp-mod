exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40020dce,0x40020fb0),(0x400204c0,0x400206b2),(0x40032550,0x400325a0),(0x40032816,0x40032860),(0x4009d4f0,0x4009d660)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/track-binding.txt').write_text('\n'.join(lines));print('\n'.join(lines))
