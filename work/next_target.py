exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40032924,0x40032a30),(0x40020600,0x400206b2),(0x4009f1f8,0x4009f35a)]:
 lines.append(f'\nWINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
for m in re.finditer(rb'[ -~]{6,}',b):
 if m.group() in [b'5Track',b'8Track',b'Kit',b'KitActive'] or re.search(rb'ZN5TrackC[12]',m.group()):lines.append(f'TYPE {base+m.start():08x} {m.group().decode()}')
for address in [0x80005434,0x80005436,0x80005437,0x80005444]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/next-target.txt').write_text('\n'.join(lines));print('\n'.join(lines))
