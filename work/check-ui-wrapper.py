exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x400d6ee4,0x400d6fb0),(0x400cc7e8,0x400cc876),(0x400d1350,0x400d138c)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:10} {i.op_str}')
