exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009e274,0x4009e398),(0x40097974,0x40097b04),(0x400df3f0,0x400df520),(0x400e114a,0x400e126a)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/held-note-release.txt').write_text('\n'.join(lines));print('\n'.join(lines))
