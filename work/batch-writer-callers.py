exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for t in [0x400089fa,0x40008b70,0x4000add6,0x4000af40,0x4000b0e8,0x4001330c]:
 out.append(f'TARGET {t:08x}')
 for k,i in enumerate(ins):
  if f'${t:x}' in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-4):k+3])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
pathlib.Path('work/batch-writer-callers.txt').write_text('\n'.join(out));print('\n'.join(out))
