exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40029546,0x40029760),(0x400094aa,0x400095d0),(0x4006f0fe,0x4006f57e)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):
  if s==0x4006f0fe and not any(x in i.op_str for x in ['4006f','401b','419a']):continue
  print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
