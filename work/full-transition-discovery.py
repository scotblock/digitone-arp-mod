exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x40001632,0x40001696),(0x400d7a6e,0x400d7bcc),(0x400d6944,0x400d695c),(0x400d6aba,0x400d6acc),(0x400ae4b0,0x400ae502)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
