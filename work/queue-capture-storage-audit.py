exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for target in [0x41342150,0x4009461c,0x431dbfb8,0x431dc4b8,0x431dc4bc,0x431dc4c0,0x431dc4c4]:
 for m in re.finditer(re.escape(struct.pack('>I',target)),b):
  pos=m.start()
  lines.append(f'RAW {target:08x} @{base+pos:08x} {b[max(0,pos-8):pos+8].hex()}')
for s,e in [(0x4009cb42,0x4009cb98),(0x40094984,0x40094a80),(0x400efc56,0x400efcb0),(0x400efef6,0x400eff6a),(0x400f002c,0x400f0080)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/queue-capture-storage-audit.txt').write_text('\n'.join(lines));print('\n'.join(lines))
