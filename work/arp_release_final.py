exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009743e,0x4009755e),(0x400df680,0x400df718),(0x400388da,0x4003893c),(0x40093400,0x40093470),(0x400e11bc,0x400e126a)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/arp-release-final.txt').write_text('\n'.join(lines));print('\n'.join(lines))
