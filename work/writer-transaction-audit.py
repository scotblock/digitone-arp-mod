exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for target in [0x40034a8c,0x40034c78,0x40035150,0x40035268,0x40013300]:
 lines.append(f'RAW REFS {target:08x} '+','.join(f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',target)),b)))
 for off in range(0,0x170000-4,2):
  if b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('4efa'),bytes.fromhex('6100'),bytes.fromhex('6000')]:
   if base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:lines.append(f'PC REF {target:08x} {base+off:08x}')
for s,e in [(0x40034a8c,0x40034ae4),(0x40035268,0x400352e4),(0x40034d2c,0x40034d98),(0x40035394,0x40035400),(0x4013017c,0x40130194)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/writer-transaction-audit.txt').write_text('\n'.join(lines));print('\n'.join(lines))
