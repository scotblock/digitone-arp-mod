exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for start,end in [(0x400d762a,0x400d78d6),(0x4012f8e8,0x4012f91e),(0x40001a4c,0x40001b08),(0x400d6aba,0x400d6adc)]:
 out.append('ENTRY '+hex(start))
 for i in md.disasm(b[start-base:end-base],start):out.append(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
pathlib.Path('work/page-dispatch-lock-discovery.txt').write_text('\n'.join(out));print('\n'.join(out))
