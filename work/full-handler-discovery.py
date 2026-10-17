exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400dc758,0x400dc90c),(0x400dc406,0x400dc432),(0x400e114a,0x400e11aa),(0x40093b72,0x40093bd4),(0x400dc530,0x400dc758)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
