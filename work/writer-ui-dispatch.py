exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400d6500,0x400d7400),(0x40156d0a,0x40156d96)]:
 for i in md.disasm(b[s-base:e-base],s):
  if '$34(' in i.op_str or '$38(' in i.op_str or 'sr' in i.op_str:out.append(f'{i.address:08x} {i.mnemonic:10} {i.op_str}')
for s,e in [(0x400b6924,0x400b6b16),(0x400d6a02,0x400d6b5e)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-ui-dispatch.txt').write_text('\n'.join(out));print('\n'.join(out))
