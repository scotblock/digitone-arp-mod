exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x4012fc1e,0x4012fc46),(0x400ababe,0x400abc10)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
