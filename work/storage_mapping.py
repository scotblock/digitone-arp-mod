exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40039c90,0x40039d50),(0x400dc418,0x400dc49a),(0x40022502,0x40022520),(0x40029a92,0x40029b10),(0x400237b0,0x40023800),(0x4001b16e,0x4001b1e0),(0x4009de28,0x4009de94)]:
 lines.append(f'\nWINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/storage-mapping.txt').write_text('\n'.join(lines));print('\n'.join(lines))
