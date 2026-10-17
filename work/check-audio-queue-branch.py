exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for i in md.disasm(b[0x4009c9e0-base:0x4009ca40-base],0x4009c9e0):print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
