exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x40000564,0x400005a0),(0x4008c7c0,0x4008c7f4)]:
 print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
print('count',int.from_bytes(b[0x40241ab4-base:0x40241ab8-base],'big'))
