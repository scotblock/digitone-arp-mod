exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x400dab8c,0x400dabd0),(0x400da900,0x400dab8c),(0x4012b344,0x4012b450)]:
 print('WINDOW',hex(lo))
 print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
