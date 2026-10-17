exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x400a8d90,0x400a8dc2),(0x401387a4,0x401387d0),(0x40138354,0x4013835e)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
for v in [0x40174d40,0x40175004]:
 print('VTABLE',hex(v))
 for j in range(-12,0x34,4):print(hex(j),hex(struct.unpack_from('>I',b,v-base+j)[0]))
