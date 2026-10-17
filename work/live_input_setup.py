exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400efa50,0x400efb32),(0x4009719e,0x40097280),(0x40097370,0x4009743e)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x4009719e,0x400ef954,0x400ef990,0x400ef810,0x400ef83c,0x400ef8b2,0x400ef9f6,0x400ee6c4]:
 lines.append(f'ABS REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/live-input-setup.txt').write_text('\n'.join(lines));print('\n'.join(lines))
