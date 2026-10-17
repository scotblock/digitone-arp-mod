exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for target in [0x400d8180,0x400d7dfe]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)];out.append(f'REFS {target:08x}: '+','.join(f'{r:08x}' for r in refs))
 for r in refs:
  out.append(b[r-base-16:r-base+8].hex())
for i in md.disasm(b[0x400d7dfe-base:0x400d8170-base],0x400d7dfe):
 if 'sr' in i.op_str or i.mnemonic in ('jsr','jmp'):out.append(f'{i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/writer-dispatch-owner.txt').write_text('\n'.join(out));print('\n'.join(out))
