exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for t in [0x40008de0,0x400134e4,0x400333ce,0x4000aeac,0x4000b058,0x4000b1c4]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-7):k+5])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
for k,i in enumerate(ins):
 if any(v in i.op_str for v in ['#$1611d','$1611d.l','#$16119']):
  out.append('SIZE CANDIDATE');out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-6):k+9])
pathlib.Path('work/batch-bulk-callers.txt').write_text('\n'.join(out));print('\n'.join(out))
