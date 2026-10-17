exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for target in [0x40014678]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)];print(f'REFS {target:08x}: '+','.join(f'{r:08x}' for r in refs))
 for r in refs:
  if r<0x40170000:
   for i in md.disasm(b[r-base-14:r-base+14],r-14):print(f'{i.address:08x} {i.mnemonic:10} {i.op_str}')
  else:
   for off in range(-32,32,4):print(f'{r+off:08x} {struct.unpack_from(">I",b,r-base+off)[0]:08x}')
