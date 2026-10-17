exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for target in [0x400d6efc,0x400b6b16]:
 refs=[base+m.start() for m in re.finditer(re.escape(struct.pack('>I',target)),b)]
 print(f'REFS {target:08x}: '+','.join(f'{r:08x}' for r in refs))
for s,e in [(0x4009e270,0x4009e310)]:
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
