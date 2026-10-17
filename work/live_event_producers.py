exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009bd30,0x4009bea0),(0x400efb00,0x400efc14),(0x40093866,0x40093920),(0x40093940,0x40093a30),(0x400948c0,0x40094910),(0x400942d0,0x40094308)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/live-event-producers.txt').write_text('\n'.join(lines));print('\n'.join(lines))
