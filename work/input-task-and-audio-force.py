exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x4001696a,0x400169d4),(0x4009ba1c,0x4009bab0),(0x400017a0,0x4000185e)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for target in [0xfc04c010,0xfc04c07f,0xfc04c008,0xfc04c01c,0xfc04c01d,0x400002fc]:
 out.append(f'REFS {target:08x} '+','.join(hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',target)),b)))
pathlib.Path('work/input-task-and-audio-force.txt').write_text('\n'.join(out));print('\n'.join(out))
