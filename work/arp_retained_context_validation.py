exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400efc16,0x400efc64),(0x4009b600,0x4009b72a),(0x4009ddae,0x4009de30),(0x40093808,0x40093866)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/arp-retained-context-validation.txt').write_text('\n'.join(lines));print('\n'.join(lines))
