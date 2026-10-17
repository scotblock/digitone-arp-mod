exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40013900,0x40013a40),(0x4002235a,0x400223b0),(0x4006f57e,0x4006f7f4),(0x400d0d16,0x400d0e10),(0x4000e3a0,0x4000e3ea)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
