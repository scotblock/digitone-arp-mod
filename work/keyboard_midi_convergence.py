exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4003893c,0x400389cc),(0x40045962,0x40045a10),(0x400df718,0x400df868),(0x400dc100,0x400dc1bc),(0x40097014,0x400970b0),(0x4009dd48,0x4009ddc2)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/keyboard-midi-convergence.txt').write_text('\n'.join(lines));print('\n'.join(lines))
