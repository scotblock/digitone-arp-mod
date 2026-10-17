exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for target in ['404dc2fc','41342150','4199cd20','400002fc']:
 out.append('GLOBAL '+target)
 for k,i in enumerate(ins):
  if '$'+target in i.op_str:out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-3):k+3])
pathlib.Path('work/outer-protection-global-guards.txt').write_text('\n'.join(out));print('\n'.join(out))
