exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for vt in [0x4017653c,0x401761c0,0x40174dfc,0x40174a08,0x401764c8,0x40173e14]:
 out.append(f'VTABLE {vt:08x}')
 for off in range(0,0x14,4):
  p=struct.unpack_from('>I',b,vt-base+off)[0];out.append(f' slot {off:02x}: {p:08x}')
  if off in [8,12,16] and base<=p<0x40170000:
   for i in md.disasm(b[p-base:p-base+400],p):
    out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
    if i.mnemonic=='rts' or i.mnemonic=='jmp':break
for s,e in [(0x4013b2d4,0x4013b390),(0x4003514a,0x40035150)]:
 out.append(f'WINDOW {s:08x}');out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/cleanup-vtables-resolved.txt').write_text('\n'.join(out));print('\n'.join(out))
