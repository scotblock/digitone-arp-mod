exec(open('work/disassemble.py').read().split('out=[]')[0])
lines=[]
for start,end in [(0x4009df6a,0x4009e010),(0x4009e720,0x4009e9c0)]:
 lines.append(f'\nWINDOW {start:08x}')
 for i in md.disasm(b[start-base:end-base],start):lines.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
# Find references to the scale-name pointer table and its neighbours.
for addr in [0x40200398,0x40200390,0x40200380,0x401c282a]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',addr)),b)]
 lines.append(f'REFS {addr:08x}: {[hex(x) for x in refs]}')
for off in range(0x1fff40,0x200070,4):
 v=struct.unpack_from('>I',b,off)[0]
 if base<=v<base+len(b):
  end=b.find(b'\0',v-base)
  s=b[v-base:end]
  if 0<len(s)<80 and all(32<=x<127 for x in s):lines.append(f'SCALE TABLE {base+off:08x} -> {v:08x} {s.decode()}')
pathlib.Path('work/pitch-flow.txt').write_text('\n'.join(lines));print('\n'.join(lines))
