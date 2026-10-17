exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009cef0,0x4009d080),(0x4009da90,0x4009dc50),(0x40095132,0x400951d8),(0x40095568,0x400955e2),(0x40093bd4,0x40093c26)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/arp-channel-dispatch.txt').write_text('\n'.join(lines));print('\n'.join(lines))
