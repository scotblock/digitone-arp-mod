exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40025250,0x40025454),(0x4003b400,0x4003b4ac),(0x40177b70,0x40177c00),(0x40025796,0x40025850),(0x40019cf0,0x40019d60),(0x400a9ca4,0x400a9ccc)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
ins=list(md.disasm(b[:0x170000],base))
for t in [0x4003b4ac,0x40025ada,0x40025250]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-7):k+5])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
pathlib.Path('work/outer-protection-dispatch.txt').write_text('\n'.join(out));print('\n'.join(out))
