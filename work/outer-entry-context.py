exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x40130cd8,0x40130d20),(0x40016438,0x40016534),(0x400d695c,0x400d6966),(0x400d6624,0x400d6730)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
