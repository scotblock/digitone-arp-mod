exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
out=[]
windows=[(0x4009dc5e,0x4009dd80),(0x4009bd8a,0x4009bde8),
 (0x400efb30,0x400efc4e),(0x400eff9c,0x400f0030),
 (0x400ef9d0,0x400efa20),(0x4009339c,0x40093454),
 (0x400f0690,0x400f06d4),(0x40095230,0x40095274)]
for s,e in windows:
 out.append(f'WINDOW {s:08x}')
 out.extend(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
for v in [0x4009bd8a,0x400f0690,0x400efa20,0x400ec23c]:
 hits=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',v)),b)]
 out.append(f'RAW REFS {v:08x}: '+','.join(f'{x:08x}' for x in hits))
pathlib.Path('work/producer-copy-remap-audit.txt').write_text('\n'.join(out))
print('\n'.join(out[:-1]))
