exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009755e,0x40097596),(0x40097596,0x40097848)]:
 lines.append(f'\nWINDOW {start:x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
target=0x4009755e
for m in re.finditer(re.escape(struct.pack('>I',target)),b):lines.append(f'ABS REF {base+m.start():08x}')
for off in range(0,len(b[:0x170000])-4,2):
 if b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100')]:
  dest=base+off+2+struct.unpack_from('>h',b,off+2)[0]
  if dest==target:lines.append(f'PC REF {base+off:08x}')
pathlib.Path('work/arp-engine.txt').write_text('\n'.join(lines));print('\n'.join(lines))

