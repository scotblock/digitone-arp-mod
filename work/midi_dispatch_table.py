exec(open('work/disassemble.py').read().split('out=[]')[0])
for i in md.disasm(b[0x400db140-base:0x400db1d6-base],0x400db140):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
