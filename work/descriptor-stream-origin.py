exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x40003338,0x40003590),(0x400036f6,0x40003830),(0x40005f62,0x40006034),(0x400039f8,0x40003a30)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
for target in [0x4000338e,0x400036f6,0x40003764,0x4024b2b8,0x4024b298,0x4024b258,0x4024b260]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)]
 lines.append(f'RAW REFS {target:08x} '+','.join(f'{x:08x}' for x in refs))
pathlib.Path('work/descriptor-stream-origin.txt').write_text('\n'.join(lines));print('\n'.join(lines))
