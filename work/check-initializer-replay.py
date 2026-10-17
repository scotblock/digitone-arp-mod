exec(open('work/disassemble.py').read().split('out=[]')[0])
print('\n'.join(f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in md.disasm(b[0x400f0504-base:0x400f05d6-base],0x400f0504)))
