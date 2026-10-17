exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for t in [0x4001fc74]:
 for m in re.finditer(re.escape(struct.pack('>I',t)),b):
  a=base+m.start();print(hex(a),'possible table',hex(a-0x24))
  for k in range(m.start()-12,m.start()+20,4):print(hex(base+k),hex(struct.unpack_from('>I',b,k)[0]))
for s,e in [(0x40134ffa,0x40135038),(0x40008aa0,0x40008b24)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
