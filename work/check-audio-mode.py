exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for i in md.disasm(b[0x40007224-base:0x40007248-base],0x40007224):print(f'{i.address:08x} {i.mnemonic:10} {i.op_str}')
