exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for target in [0x4002235a,0x4009461c,0x401a498c,0x401a4990,0x401a48f0,0x401a4900]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)];out.append(f'REFS {target:08x}: '+','.join(f'{r:08x}' for r in refs))
 for r in refs:
  for i in md.disasm(b[r-base-10:r-base+22],r-10):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for s,e in [(0x40093b72,0x40093bc2),(0x40093b30,0x40093b72)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-active-alias.txt').write_text('\n'.join(out));print('\n'.join(out))
