exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[];ins=list(md.disasm(b[:0x170000],base))
for t in [0x40177ba8,0x4002528c,0x4003c8a0,0x4003b576]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-7):k+6])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
for s,e in [(0x4003c8a0,0x4003c930),(0x400d6974,0x400d6aba),(0x4003b576,0x4003b600),(0x400ac130,0x400ac1b0),(0x40144554,0x401445a6)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/outer-protection-ui.txt').write_text('\n'.join(out));print('\n'.join(out))
