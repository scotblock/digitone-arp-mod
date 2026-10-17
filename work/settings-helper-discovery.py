exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for i in md.disasm(b[0x4009c2f8-base:0x4009c314-base],0x4009c2f8):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
