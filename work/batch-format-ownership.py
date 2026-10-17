exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400088ca,0x400089fa),(0x40008ca4,0x40009030),(0x4000aeac,0x4000af40),(0x4000b058,0x4000b0e8),(0x4000b1c4,0x4000b240),(0x4001341c,0x40013590),(0x40033390,0x40033410)]:
 out.append(f'WINDOW {s:08x}')
 out.extend(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
pathlib.Path('work/batch-format-ownership.txt').write_text('\n'.join(out));print('\n'.join(out))
