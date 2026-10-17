exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4002081c,0x400208f0),(0x40022574,0x400225ec),(0x400242d0,0x400243bc),(0x400254b0,0x40025580),(0x40025610,0x40025730),(0x400ec23c,0x400ec284),(0x4000b240,0x4000b258)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
for t in [0x400333ce,0x400208a0]:
 for m in re.finditer(re.escape(struct.pack('>I',t)),b):
  a=base+m.start();out.append(f'POINTER {t:x} AT {a:x}');out.extend(f'{base+k:08x}: {struct.unpack_from(">I",b,k)[0]:08x}' for k in range(m.start()-24,m.start()+28,4))
pathlib.Path('work/batch-bulk-ownership.txt').write_text('\n'.join(out));print('\n'.join(out))
