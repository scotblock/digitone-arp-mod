exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400b6f62,0x400b6fb0),(0x4009c838,0x4009c8b0)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for target in [0x400d6974,0x4009c838]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)];out.append(f'REFS {target:08x}: '+','.join(f'{r:08x}' for r in refs))
pathlib.Path('work/writer-ui-entry.txt').write_text('\n'.join(out));print('\n'.join(out))
