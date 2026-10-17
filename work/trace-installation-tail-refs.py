exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for lo,hi in [(0x40005180,0x40005220),(0x40001df4,0x40001e34)]:
 print('WINDOW',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
print('refs tail:')
for p in range(0,len(b)-3,2):
 v=int.from_bytes(b[p:p+4],'big')
 if 0x40241b00<=v<=0x40242000:print(hex(base+p),hex(v))
