exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400dea02,0x400deb80),(0x400e0f9e,0x400e1052),(0x400e0f4e,0x400e0f9e)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x400e1052,0x400e10d6,0x41962008,0x41962050]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/sustain-controller.txt').write_text('\n'.join(lines));print('\n'.join(lines))
