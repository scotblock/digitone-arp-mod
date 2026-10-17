exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400e0e96,0x400e0f9e),(0x40095ece,0x40095f3c),(0x40126618,0x40126640),(0x40001cda,0x40001e30),(0x400dc532,0x400dc758),(0x400dc758,0x400dc90c),(0x400d6d46,0x400d6db6),(0x400ae9fa,0x400aebc0)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
