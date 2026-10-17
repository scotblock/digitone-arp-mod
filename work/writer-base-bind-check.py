exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40136658,0x401366e0),(0x40135386,0x40135402),(0x4013a886,0x4013a902)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):
  print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
  if i.mnemonic=='rts':break
