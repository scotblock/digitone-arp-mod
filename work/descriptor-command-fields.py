exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
lines=[]
for s,e in [(0x40095d96,0x40095e80),(0x400013cc,0x40001452),(0x40007224,0x40007346)]:
 lines.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):lines.append(f'{i.address:08x} {i.bytes.hex():18} {i.mnemonic:12} {i.op_str}')
for v in [0x8000ba00,0x4016cfe0,0x400efc50]:
 lines.append(f'RAW REFS {v:08x} '+','.join(f'{base+m.start():08x}' for m in re.finditer(re.escape(struct.pack('>I',v)),b)))
lines.append('USB PRIME MASKS '+','.join(hex(x) for x in struct.unpack_from('>8I',b,0x4016cfe0-base)))
pathlib.Path('work/descriptor-command-fields.txt').write_text('\n'.join(lines));print('\n'.join(lines))
