exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x4000579e,0x400057b4),(0x40030e1e,0x40030e36),(0x40032436,0x4003244c),(0x40129f82,0x40129f98)]:
 print(hex(lo),b[lo-base:hi-base].hex());print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
