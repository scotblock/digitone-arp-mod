exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x4006f82a,0x4006f880),(0x40022502,0x40022510),(0x40136086,0x40136090),(0x400a8dda,0x400a8de4)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
