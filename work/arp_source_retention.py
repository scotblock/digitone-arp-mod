exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009ccdc,0x4009cef0),(0x4009de94,0x4009df6a),(0x40094796,0x40094870),(0x400f074c,0x400f0810)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/arp-source-retention.txt').write_text('\n'.join(lines));print('\n'.join(lines))
