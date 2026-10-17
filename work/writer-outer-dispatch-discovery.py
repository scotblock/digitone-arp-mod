exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x400d0900,0x400d1600),(0x400ca000,0x400cf000)]:
 for i in md.disasm(b[s-base:e-base],s):
  if (i.mnemonic=='movea.l' and '$8(' in i.op_str) or 'sr' in i.op_str:out.append(f'{i.address:08x} {i.mnemonic:10} {i.op_str}')
for i in md.disasm(b[0x400b6f62-base:0x400b7240-base],0x400b6f62):
 if 'sr' in i.op_str:out.append(f'SCREEN MASK {i.address:08x} {i.mnemonic} {i.op_str}')
pathlib.Path('work/writer-outer-dispatch-discovery.txt').write_text('\n'.join(out));print('\n'.join(out))
