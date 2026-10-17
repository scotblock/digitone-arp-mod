exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400d6aba,0x400d6ae0),(0x400d75fe,0x400d7620),(0x4012c2fe,0x4012c344)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
