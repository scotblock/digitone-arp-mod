exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400945e0,0x40094758),(0x400955c0,0x40095730),(0x40094308,0x400944c8),(0x4009dd48,0x4009ddaE)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x41342154,0x41342158,0x4134215c,0x41342160,0x400945e0]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/pattern-switch.txt').write_text('\n'.join(lines));print('\n'.join(lines))
