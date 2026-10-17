exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x400d5eca,0x400d5f08),(0x400d5880,0x400d58d2),(0x4006fb20,0x4006fb94),(0x400d6a02,0x400d6aba)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
