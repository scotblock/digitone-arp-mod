exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40095458,0x40095548),(0x40095b6e,0x40095bd6),(0x400936c0,0x400937be)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/per-track-pattern-cache.txt').write_text('\n'.join(lines));print('\n'.join(lines))
