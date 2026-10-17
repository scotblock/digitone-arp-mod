exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400206b2,0x40020740),(0x4002377a,0x400237b0),(0x4009722c,0x4009743e),(0x4009de2a,0x4009de94),(0x4009f0f4,0x4009f200)]:
 lines.append(f'\nWINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/track-mapping.txt').write_text('\n'.join(lines));print('\n'.join(lines))
