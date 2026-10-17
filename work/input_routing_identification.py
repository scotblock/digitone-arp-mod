exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x400df50a,0x400df680),(0x400387d0,0x400388e4)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for target in [0x400df584,0x400dc18a,0x400388e4,0x400df5ec]:
 lines.append(f'REFS {target:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",target)),b)]}')
pathlib.Path('work/input-routing-identification.txt').write_text('\n'.join(lines));print('\n'.join(lines))
