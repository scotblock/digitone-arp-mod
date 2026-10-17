exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for target in [0x407b00b0,0x41311400,0x4131b980,0x40013722]:
 print('REFS',hex(target));needle=target.to_bytes(4,'big');pos=0
 while True:
  pos=b.find(needle,pos)
  if pos<0:break
  print(hex(base+pos),b[max(pos-4,0):pos].hex());pos+=1
for s,e in [(0x400d5f02,0x400d5fd0),(0x4006fc62,0x4006fd30),(0x4006f040,0x4006f080)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
