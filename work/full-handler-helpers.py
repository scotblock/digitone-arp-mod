exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x40106c30,0x40106dc0),(0x400e0f9e,0x400e114a),(0x400e114a,0x400e1230),(0x40095d98,0x40095ed0),(0x400db642,0x400db758),(0x4009e39e,0x4009e3d0),(0x400d653a,0x400d6610),(0x400dc432,0x400dc530)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
print('gate refs')
for a in [0x4131ba40,0x4131ba1c]:
 needle=a.to_bytes(4,'big');pos=0
 while True:
  pos=b.find(needle,pos)
  if pos<0:break
  print(hex(a),hex(base+pos));pos+=1
