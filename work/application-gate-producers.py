exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40013722,0x400138de),(0x400d5b18,0x400d5c10),(0x4006ecf4,0x4006ed72),(0x4006f7e0,0x4006f830)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
print('application vtable')
for k in range(0,0xb0,4):print(hex(k),hex(struct.unpack_from('>I',b,0x40182a28-base+k)[0]))
