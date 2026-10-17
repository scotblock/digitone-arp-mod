exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for target in [0x40093c26,0x40093fc8,0x400f0626,0x4009461c,0x40093b84]:
 refs=[]
 for off in range(0,0x170000-6,2):
  if b[off:off+2] in [bytes.fromhex('4eb9'),bytes.fromhex('4ef9')] and struct.unpack_from('>I',b,off+2)[0]==target:refs.append(base+off)
  elif b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100'),bytes.fromhex('6000')] and base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.append(base+off)
 lines.append(f'CALL/JUMP REFS {target:08x}: {[hex(x) for x in refs]}')
for address in [0x413421cc,0x413421d0,0x40188edc]:
 lines.append(f'ABS REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
pathlib.Path('work/event-producer-refs.txt').write_text('\n'.join(lines));print('\n'.join(lines))
