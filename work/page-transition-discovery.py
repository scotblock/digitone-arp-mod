exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for start,end in [(0x400d7400,0x400d7640),(0x400509cc,0x40050a12),(0x400b697a,0x400b69ac),(0x400ae79c,0x400ae822)]:
 out.append('WINDOW '+hex(start))
 for i in md.disasm(b[start-base:end-base],start):out.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/page-transition-discovery.txt').write_text('\n'.join(out));print('\n'.join(out))
