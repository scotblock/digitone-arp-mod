exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x40093b72,0x40093c10),(0x40134fda,0x40135030),(0x400dc432,0x400dc4e0),(0x4009e720,0x4009e840),(0x4009dc50,0x4009dcb0)]:
 lines.append(f'WINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for address in [0x401fdf18,0x401fdf38,0x401fdf58,0x41345ebc]:
 lines.append(f'REFS {address:08x} {[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack(">I",address)),b)]}')
for address in [0x401764c8,0x40173e14]:
 lines.append(f'VTABLE {address:08x} '+str([hex(struct.unpack_from('>I',b,address-base+n)[0]) for n in range(0,48,4)]))
pathlib.Path('work/track-binding-validation.txt').write_text('\n'.join(lines));print('\n'.join(lines))
