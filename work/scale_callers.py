exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40039d40,0x40039e10),(0x400dc440,0x400dc480),(0x4009e9ba,0x4009f052)]:
 lines.append(f'\nWINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/scale-callers.txt').write_text('\n'.join(lines));print('\n'.join(lines))
