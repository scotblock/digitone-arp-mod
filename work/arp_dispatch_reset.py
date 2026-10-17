exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009cb98,0x4009ccb0),(0x400f05d6,0x400f0626),(0x400f0626,0x400f0690),(0x400f0690,0x400f06d4),(0x40097848,0x400978a4),(0x400970b0,0x40097140)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/arp-dispatch-and-reset.txt').write_text('\n'.join(lines));print('\n'.join(lines))
