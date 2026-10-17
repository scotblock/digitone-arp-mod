exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x40003830,0x40003a00),(0x4000420c,0x40004550)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
for target in [0x40003830,0x4000420c,0x400043ea]:
 refs=set(base+m.start()-2 for m in re.finditer(re.escape(struct.pack('>I',target)),b) if b[m.start()-2:m.start()] in [bytes.fromhex('4eb9'),bytes.fromhex('4ef9')])
 for off in range(0,0x170000-4,2):
  if b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100')]:
   if base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.add(base+off)
 lines.append(f'CALL REFS {target:08x}: '+','.join(f'{x:08x}' for x in sorted(refs)))
for off in range(0,0x170000-6,2):
 op=struct.unpack_from('>H',b,off)[0]
 if (op&0xf03f)==0x103c and b[off+2:off+4]==bytes.fromhex('00ec'):
  ins=next(md.disasm(b[off:off+12],base+off),None)
  lines.append(f'EC BYTE CANDIDATE {base+off:08x} {ins.mnemonic} {ins.op_str}')
pathlib.Path('work/descriptor-producer.txt').write_text('\n'.join(lines));print('\n'.join(lines))
