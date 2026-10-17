exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for target in [0x400efcb8,0x431dc4c4,0x431dc4c0,0x431dc4bc]:
 refs=set(base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b))
 if target == 0x400efcb8:
  for off in range(0,0x170000-4,2):
   if b[off:off+2] in [bytes.fromhex('4eba'),bytes.fromhex('6100')]:
    if base+off+2+struct.unpack_from('>h',b,off+2)[0]==target:refs.add(base+off)
 lines.append(f'REFS {target:08x} '+','.join(f'{x:08x}' for x in sorted(refs)))
for s,e in [(0x400efc50,0x400efcb0),(0x4009cb98,0x4009cc20),(0x4009e008,0x4009e01a)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/queue-caller-refs.txt').write_text('\n'.join(lines));print('\n'.join(lines))
