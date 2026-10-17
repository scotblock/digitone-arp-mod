exec(open('work/disassemble.py').read().split('out=[]')[0])
for start,end in [(0x400f0440,0x400f0508)]:
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
