exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for target in [0x400388e4,0x400df63c,0x400dc432,0x400dc18a]:
 refs=[]
 for off in range(0,0x170000-6,2):
  if b[off:off+2] in [bytes.fromhex('4eb9'),bytes.fromhex('4ef9')] and struct.unpack_from('>I',b,off+2)[0]==target:refs.append(base+off)
  elif b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100'),bytes.fromhex('6000')] and base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.append(base+off)
 lines.append(f'CALL REFS {target:08x} {[hex(x) for x in refs]}')
for start,end in [(0x400385a0,0x40038660),(0x400df176,0x400df1b8),(0x400e1050,0x400e1114),(0x400389cc,0x40038a7c)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/live-input-upstream.txt').write_text('\n'.join(lines));print('\n'.join(lines))
