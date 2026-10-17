exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400d6b90,0x400d6bbc),(0x400d798a,0x400d7a6e),(0x4012e9a8,0x4012e9da),(0x40167298,0x401672c4),(0x40001b6e,0x40001c0c),(0x4012f8e8,0x4012f900)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
