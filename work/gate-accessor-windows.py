exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40082a00,0x40082b7a),(0x4009e0ac,0x4009e120),(0x40015b9c,0x40015c10),(0x4000e040,0x4000e0b0),(0x400d5c0a,0x400d5d90)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
