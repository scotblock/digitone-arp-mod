exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x400dc4aa,0x400dc4b8),(0x40093ed0,0x40093f24),(0x4009df70,0x4009dfb2),(0x40106b6c,0x40106be2)]:
 print('WINDOW',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
