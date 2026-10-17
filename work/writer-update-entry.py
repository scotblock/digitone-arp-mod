exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40016d56,0x40016eb0),(0x4001773a,0x40017760),(0x40017c40,0x40017c9a)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for t in [0x40016d56]:
 out.append('REFS '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',t)),b)))
pathlib.Path('work/writer-update-entry.txt').write_text('\n'.join(out));print('\n'.join(out))
