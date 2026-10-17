exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for target in [0x40507e2c,0x400b6d92,0x400b6e7a,0x40094612,0x40094652,0x400945f0]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)]
 out.append(f'REFS {target:08x}: '+','.join(f'{r:08x}' for r in refs))
 for ref in refs:
  if target in (0x40507e2c,0x400b6d92,0x400b6e7a):
   start=ref-8
   if target==0x40507e2c:
    for i in md.disasm(b[start-base:ref-base+28],start):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
   else:out.append(b[ref-base-20:ref-base+24].hex())
for s,e in [(0x400945e0,0x40094668),(0x40031c50,0x40031c66),(0x400a9ca4,0x400a9cee)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-dispatch-refs.txt').write_text('\n'.join(out));print('\n'.join(out))
