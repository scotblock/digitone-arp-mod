exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for s,e in [(0x40022366,0x40022432),(0x40136090,0x401360ae),(0x40134ffa,0x40135010),(0x401764c8,0x40176500)]:
 out.append(f'WINDOW {s:08x}')
 if s==0x401764c8:
  out.extend(f'{s+x:08x}: {struct.unpack_from(">I",b,s-base+x)[0]:08x}' for x in range(0,e-s,4));continue
 for i in md.disasm(b[s-base:e-base],s):out.append(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
pathlib.Path('work/writer-bank-bind.txt').write_text('\n'.join(out));print('\n'.join(out))
