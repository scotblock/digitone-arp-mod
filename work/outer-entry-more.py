exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400d6af2,0x400d6b3a),(0x400d6b62,0x400d6b90),(0x40130c4e,0x40130c70),(0x40016408,0x40016440),(0x4012f8e8,0x4012f908)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
print('vtable')
for k in range(0,0x34,4):print(hex(k),hex(struct.unpack_from('>I',b,0x401a3ba8-base+k)[0]))
