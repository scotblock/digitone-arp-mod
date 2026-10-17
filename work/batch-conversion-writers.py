exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400089fa,0x40008b70),(0x40008b70,0x40008cac),(0x4000add6,0x4000aeac),(0x4000af40,0x4000b058),(0x4000b0e8,0x4000b1c0),(0x4001330a,0x40013370)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/batch-conversion-writers.txt').write_text('\n'.join(out));print('\n'.join(out))
