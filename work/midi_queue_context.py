exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for address in [0x400d961a,0x400dc09e,0x400d95f0]:
 lines.append(f'ABS REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
for start,end in [(0x400d9990,0x400d9ab0),(0x400db1d0,0x400db34c)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/midi-queue-context.txt').write_text('\n'.join(lines));print('\n'.join(lines))
