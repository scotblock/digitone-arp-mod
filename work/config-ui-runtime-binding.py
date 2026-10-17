exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40029800,0x40029a30),(0x40029a30,0x40029d00)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
print('CONFIG OFFSETS CANDIDATES')
for pos in range(0x28000,0x2e000,2):
 for disp in ['008c','00b0']:
  if b[pos:pos+2].hex()==disp:
   i=next(md.disasm(b[pos-2:pos+8],base+pos-2,count=1),None)
   if i and ('$8c(' in i.op_str or '$b0(' in i.op_str):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
