exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4001fc74,0x4001fdc0),(0x40020fb0,0x400210e0),(0x40031c60,0x40031d54),(0x400f02b4,0x400f02d6)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x4001fc74,0x400f02b4,0x80003f8c,0x4199d570]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/pattern-binding.txt').write_text('\n'.join(lines));print('\n'.join(lines))
