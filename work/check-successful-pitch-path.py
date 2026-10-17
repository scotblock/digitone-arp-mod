exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x40097818,0x400978b8),(0x4009df0a,0x4009df78)]:
 print('WINDOW',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
