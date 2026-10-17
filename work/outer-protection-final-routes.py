exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for t in [0x4003ac86,0x40144566,0x4014462a,0x400071d6,0x4000722c]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-4):k+3])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
for s,e in [(0x4012fe8e,0x4012fed8),(0x4003da6e,0x4003da8c),(0x4003e36a,0x4003e3a6),(0x400171e2,0x400172c0),(0x4014462a,0x4014466a)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/outer-protection-final-routes.txt').write_text('\n'.join(out));print('\n'.join(out))
