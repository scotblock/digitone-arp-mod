exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x40097092,0x400970b0),(0x40094cc0,0x40094dc0),(0x40095548,0x40095616),(0x400958ce,0x40095950),(0x400eeb96,0x400eebde)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
for target in [0x400efc56,0x400efcb8,0x40094cc0,0x40094dc0]:
 refs=set()
 for off in range(0,0x170000-6,2):
  if b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100')] and base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.add(base+off)
  if b[off:off+2] in [bytes.fromhex('4eb9'),bytes.fromhex('4ef9')] and struct.unpack_from('>I',b,off+2)[0]==target:refs.add(base+off)
 lines.append(f'CALL REFS {target:08x} '+','.join(f'{x:08x}' for x in sorted(refs)))
pathlib.Path('work/queue-timing-followup.txt').write_text('\n'.join(lines));print('\n'.join(lines))
