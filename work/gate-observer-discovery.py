exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x401386a8,0x40138720),(0x401387a4,0x401387b0),(0x40022502,0x4002250c),(0x4012f97a,0x4012fa36)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
