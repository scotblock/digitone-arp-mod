exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for t in [0x40022552,0x400208a0,0x40024200,0x40025628,0x400eef48,0x400eef72]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-10):k+9])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
for s,e in [(0x40025420,0x400254b8),(0x40025720,0x40025798),(0x40024280,0x400242d0),(0x400243bc,0x40024404),(0x400208a0,0x400208da)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/outer-protection-first.txt').write_text('\n'.join(out));print('\n'.join(out))
