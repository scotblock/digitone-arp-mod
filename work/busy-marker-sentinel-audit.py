exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[];ins=list(md.disasm(b[:0x170000],base))
for t in range(0x4199d508,0x4199d538,4):
 out.append(f'RAM {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-4):k+4])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
for s,e in [(0x400efc56,0x400efcb0),(0x400eff42,0x400effa4),(0x400f003a,0x400f0114),(0x4009bcf8,0x4009bd20)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/busy-marker-sentinel-audit.txt').write_text('\n'.join(out));print('\n'.join(out))
