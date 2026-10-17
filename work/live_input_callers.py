exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for target in [0x400efa20,0x4009e3cc,0x400970b0,0x400ef9f6]:
 refs=[]
 for off in range(0,0x170000-6,2):
  if b[off:off+2] in [bytes.fromhex('4eb9'),bytes.fromhex('4ef9')] and struct.unpack_from('>I',b,off+2)[0]==target:refs.append(base+off)
  elif b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100'),bytes.fromhex('6000')] and base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.append(base+off)
 lines.append(f'CALL/JUMP REFS {target:08x}: {[hex(x) for x in refs]}')
for start,end in [(0x400efc50,0x400efe10),(0x400e4322,0x400e4390),(0x400efa4c,0x400efa84),(0x4009e3cc,0x4009e492)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/live-input-callers.txt').write_text('\n'.join(lines));print('\n'.join(lines))
