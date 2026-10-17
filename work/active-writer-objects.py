exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
out=[]
for s,e in [(0x40027b86,0x40027e10),(0x40032550,0x400325d8),(0x400237b0,0x400237de),(0x400b6d92,0x400b6f78)]:
 out.append(f'WINDOW {s:08x}')
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/active-writer-objects.txt').write_text('\n'.join(out))
print('\n'.join(out[:190]))
