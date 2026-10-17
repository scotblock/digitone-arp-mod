exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for t in [0x40138354,0x4002af1a,0x4002b344,0x4002b38e]:
 print('REFS',hex(t));needle=t.to_bytes(4,'big');pos=0
 while True:
  pos=b.find(needle,pos)
  if pos<0:break
  print(hex(base+pos));pos+=1
for s,e in [(0x4013e262,0x4013e2c0),(0x4015a304,0x4015a360),(0x4012c344,0x4012c3bc),(0x40138210,0x40138260)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
