exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400d6950,0x400d6a10),(0x400d6b5e,0x400d6bd0),(0x4015a3ae,0x4015a414),(0x400ae502,0x400ae570),(0x4008dce0,0x4008dd60)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
print('VTABLE')
for k in range(0,0x78,4):print(hex(k),hex(struct.unpack_from('>I',b,0x401a3b14-base+k)[0]))
