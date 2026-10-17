exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for target in [0x400d7a6e,0x400ae9fa,0x4131b998,0x4131b9e4]:
 needle=target.to_bytes(4,'big');pos=0
 print('REFS',hex(target))
 while True:
  pos=b.find(needle,pos)
  if pos<0:break
  a=base+pos
  if pos%2==0:
   for candidate in [a-2,a-4]:
    i=next(md.disasm(b[candidate-base:candidate-base+10],candidate,count=1),None)
    if i and i.size in (6,8) and needle in i.bytes:print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
  pos+=1
for start,end in [(0x400d59dc,0x400d5b00),(0x400d6306,0x400d6330)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
