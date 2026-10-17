exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40017230,0x400172ba),(0x40011c80,0x40011d98)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
for i in md.disasm(b[0x40011b00-base:0x400172b8-base],0x40011b00):
 if 'sr' in i.op_str:out.append(f'OUTER MASK {i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/writer-main-task.txt').write_text('\n'.join(out));print('\n'.join(out))
