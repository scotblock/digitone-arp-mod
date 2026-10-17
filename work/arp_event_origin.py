exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40093d66,0x40093f90),(0x40094cde,0x40094d6a),(0x40095740,0x400957b0),(0x40095870,0x40095946),(0x4009755e,0x400975a2),(0x4009ce80,0x4009cf70)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/arp-event-origin.txt').write_text('\n'.join(lines));print('\n'.join(lines))
