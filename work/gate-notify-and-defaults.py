exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for v in [0x40174fc8,0x4017505c,0x401750c4]:
 print('VTABLE',hex(v))
 for j in range(0,0x34,4):print(hex(j),hex(struct.unpack_from('>I',b,v-base+j)[0]))
for s,e in [(0x40066750,0x400667d4),(0x40066fc0,0x40067020),(0x400094aa,0x400094ce),(0x40009cd0,0x40009d24),(0x400136a6,0x40013722)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
