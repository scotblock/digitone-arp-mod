exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for target in [0x400b6cca,0x400b6db6,0x400b6e16,0x400b6e9e,0x400b6efe]:
 candidates=[]
 for off in range(target-base-6000,target-base,2):
  if b[off:off+2]==bytes.fromhex('4e56') or b[off:off+3]==bytes.fromhex('4fefff'):candidates.append(base+off)
 lines.append(f'ENTRY CANDIDATES {target:08x} '+','.join(f'{x:08x}' for x in candidates[-3:]))
for s,e in [(0x400b6c80,0x400b6f4c),(0x40034a8c,0x40034c78),(0x40034c78,0x40034d98),(0x40035268,0x400353f8)]:
 instructions=list(md.disasm(b[s-base:e-base],s))
 lines.append(f'SR/LOCK CANDIDATE SCAN {s:08x}..{e:08x}')
 for i in instructions:
  if 'sr' in i.op_str or i.mnemonic in ('jsr','jmp'):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
 if s==0x400b6c80:
  lines.append('CALLER DETAIL')
  for i in instructions:lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/writer-caller-locks.txt').write_text('\n'.join(lines));print('\n'.join(lines[:17]))
