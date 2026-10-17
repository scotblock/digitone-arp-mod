exec(open('work/disassemble.py').read().split('out=[]')[0])
for s,e in [(0x4012f97a,0x4012fa10),(0x400237b0,0x40023810),(0x40013310,0x40013380)]:
 print(hex(s))
 for i in md.disasm(b[s-base:e-base],s):
  print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
  if i.mnemonic=='rts':break
