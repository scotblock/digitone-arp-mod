exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x4013835e,0x4013857a),(0x40022318,0x4002235a),(0x400d5c10,0x400d5c28)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
print('DESERIALIZER GATES')
for i in md.disasm(b[0x400094aa-base:0x40009d24-base],0x400094aa):
 if any(x in i.op_str for x in ['$8c(a2)','$b0(a2)']):
  p=i.address
  for j in md.disasm(b[p-base-32:p-base+8],p-32):print(f'{j.address:08x} {j.mnemonic} {j.op_str}')
for a in [0x401b9a4c,0x401bd67e,0x401b8644,0x401b8622,0x401b9a74,0x401b9a80,0x401b86fe,0x401b9a8b,0x401b9409,0x401b9a99]:print(hex(a),b[a-base:].split(b'\0',1)[0])
