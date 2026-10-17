exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for i in md.disasm(b[0x40016528-base:0x40016576-base],0x40016528):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
