exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400ded98,0x400dee64),(0x400e1052,0x400e114a),(0x400e11bc,0x400e128e),(0x4009b0de,0x4009b158)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/sustain-release-chain.txt').write_text('\n'.join(lines));print('\n'.join(lines))
