exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x400f0626,0x400f0690),(0x4009de50,0x4009df0a),(0x4009755e,0x4009764a)]:
 print('WINDOW',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
