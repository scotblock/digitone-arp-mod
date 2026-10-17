exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
ins=list(md.disasm(b[:0x170000],base));out=[]
for k,i in enumerate(ins):
 if i.mnemonic=='movea.l' and re.match(r'\$8\(a[0-6]\), a[0-6]$',i.op_str):
  reg=i.op_str[-2:]
  if any(j.mnemonic in ('jsr','jmp') and j.op_str=='('+reg+')' for j in ins[k+1:k+7]):
   out.append(f'CANDIDATE {i.address:08x}')
   out.extend(f'{j.address:08x} {j.mnemonic:10} {j.op_str}' for j in ins[max(0,k-3):k+7])
pathlib.Path('work/virtual08-dispatch-inventory.txt').write_text('\n'.join(out));print('\n'.join(out));print('COUNT',sum(x.startswith('CANDIDATE') for x in out))
