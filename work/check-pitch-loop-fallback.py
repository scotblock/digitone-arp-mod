exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
print('\n'.join(f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in md.disasm(b[0x4009dffa-base:0x4009e080-base],0x4009dffa)))
