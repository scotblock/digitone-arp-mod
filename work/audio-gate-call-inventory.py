exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for target in [0x400eef48,0x400eef72,0x4009e352,0x4009e35c]:
 out.append(f'TARGET {target:08x}')
 for k,i in enumerate(ins):
  if f'${target:x}' in i.op_str:
   out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-2):k+3])
 out.append('RAW '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',target)),b)))
for i in ins:
 if 0x40016d56<=i.address<0x40017d20 and 'sr' in i.op_str:out.append(f'INPUT MASK {i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/audio-gate-call-inventory.txt').write_text('\n'.join(out));print('\n'.join(out))
