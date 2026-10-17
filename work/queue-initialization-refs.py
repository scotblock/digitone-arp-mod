exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
target=0x400f00ea
lines.append('RAW refs '+','.join(f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',target)),b)))
for off in range(0,0x170000-6,2):
 op=struct.unpack_from('>H',b,off)[0]
 if op in [0x4eba,0x4efa,0x6100,0x6000,0x41fa,0x43fa,0x45fa,0x47fa,0x49fa,0x4bfa,0x4dfa]:
  dest=base+off+2+struct.unpack_from('>h',b,off+2)[0]
  if dest==target:lines.append(f'PC ref {base+off:08x} {b[off:off+4].hex()}')
 if op&0xff00 in (0x6000,0x6100) and op&255 not in (0,255):
  delta=op&255; delta=delta-256 if delta>=128 else delta
  if base+off+2+delta==target:lines.append(f'SHORT ref {base+off:08x}')
print('\n'.join(lines) or 'No direct or tested PC-relative references to initializer entry')
pathlib.Path('work/queue-initialization-refs.txt').write_text('\n'.join(lines))
md.skipdata=True
for i in md.disasm(b[0x400f0080-base:0x400f00f0-base],0x400f0080):
 print(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
