exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400dc1b0,0x400dc2b0),(0x400dc5c0,0x400dc750),(0x400dc432,0x400dc5c0),(0x4009c29a,0x4009c2f8),(0x4009789c,0x400978bc)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x400dc432,0x400dc1b0,0x400dc25a]:
 lines.append(f'ABS REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/live-note-origin.txt').write_text('\n'.join(lines));print('\n'.join(lines))
