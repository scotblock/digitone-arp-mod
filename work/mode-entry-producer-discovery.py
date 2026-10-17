exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400d692c,0x400d6950),(0x400d6d46,0x400d6db6),(0x400dc432,0x400dc532),(0x400db15a,0x400db300)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
