exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40093c26,0x40093d70),(0x40093fc8,0x40094070),(0x40094900,0x40094984),(0x40094d20,0x40094d90),(0x400951bC,0x4009526e),(0x40095330,0x40095442)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/event-pattern-context.txt').write_text('\n'.join(lines));print('\n'.join(lines))
