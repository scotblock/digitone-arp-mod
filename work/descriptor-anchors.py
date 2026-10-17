exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for target in [0x4024b050,0x4024b264,0x4024b040,0x4024b250,0x40003a90,0x40003830]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)]
 lines.append(f'RAW REFS {target:08x} '+','.join(f'{x:08x}' for x in refs))
for off in range(0,0x170000-8,2):
 op=struct.unpack_from('>H',b,off)[0]
 if (op&0xf100)==0x7000 and op&255==0xec or b[off:off+4] in [bytes.fromhex('ec000000'),bytes.fromhex('000000ec')]:
  lines.append(f'EC CANDIDATE {base+off:08x} '+b[max(0,off-8):off+12].hex())
for s,e in [(0x40003a2a,0x40003ba0),(0x400d9260,0x400d93a0)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/descriptor-anchors.txt').write_text('\n'.join(lines));print('\n'.join(lines))
