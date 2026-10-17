exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4003b49c,0x4003b580),(0x40025a88,0x40025b68),(0x40025c38,0x40025c78),(0x40016c10,0x40016cbc),(0x400eef48,0x400eefa4),(0x400cc74a,0x400cc7ac),(0x40169574,0x401695b4)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
ins=list(md.disasm(b[:0x170000],base))
for t in [0x400242ba,0x40025a88,0x4003b49c,0x4003b50e]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-6):k+5])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
pathlib.Path('work/outer-protection-second.txt').write_text('\n'.join(out));print('\n'.join(out))
