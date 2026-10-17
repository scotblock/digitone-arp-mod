exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40034140,0x40034280),(0x4013a33a,0x4013a390),(0x4013a886,0x4013a9f6),(0x4009f280,0x4009f380)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x40034140,0x40034160,0x4003416c,0x4013a344,0x40031c60,0x4009f2c0,0x4009f2d0,0x4009f2e0,0x4009f2f8,0x4009f308]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/track-backing.txt').write_text('\n'.join(lines));print('\n'.join(lines))
