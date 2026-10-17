exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40131922,0x4013199c),(0x40022366,0x4002242e),(0x40027b86,0x40027c30)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
