exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40039312,0x400393b4),(0x400dc090,0x400dc0e0),(0x400df870,0x400df8e0),(0x400e9f3a,0x400e9f7a)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x400388e4,0x40039312,0x400dc090,0x400df870]:
 lines.append(f'ABS REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/input-handler-evidence.txt').write_text('\n'.join(lines));print('\n'.join(lines))
