exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for target in [0x40008ac8,0x40008c5a,0x4000ae8e,0x4000b034,0x4000b19e,0x40013348,0x40034bb4,0x40034d00,0x40035356,0x400b5ea2]:
 p=target-base
 candidates=[]
 for off in range(max(0,p-800),p,2):
  if b[off:off+2] in [bytes.fromhex('4fef'),bytes.fromhex('4fef')]:continue
  if b[off:off+3]==bytes.fromhex('4fefff') or b[off:off+2]==bytes.fromhex('4e56'):
   candidates.append(base+off)
 lines.append(f'PROLOGUE CANDIDATES before {target:08x}: '+','.join(f'{x:08x}' for x in candidates[-4:]))
for s,e in [(0x40034ae0,0x40034bea),(0x40034c50,0x40034d30),(0x40035310,0x40035398),(0x40013312,0x40013380),(0x400b5e68,0x400b5f34)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/pattern-writer-contexts.txt').write_text('\n'.join(lines));print('\n'.join(lines))
