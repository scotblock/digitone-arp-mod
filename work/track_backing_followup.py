exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for address in [0x40034174,0x401764c8,0x40034100,0x400f0300]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
for start,end in [(0x400340a0,0x40034174),(0x400f02c0,0x400f03c0),(0x4009e398,0x4009e4a8),(0x400206c0,0x40020880)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/track-backing-followup.txt').write_text('\n'.join(lines));print('\n'.join(lines))
