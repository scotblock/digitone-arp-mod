exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
p=0x40241c90-base
while p>=4 and 0x40000400<=int.from_bytes(b[p-4:p],'big')<0x4016b600:p-=4
print('pointer run begins',hex(base+p),'entries',(0x40241c94-base-p)//4,'preceding',b[p-16:p+16].hex())
v=base+p
for q in re.finditer(re.escape(v.to_bytes(4,'big')),b):
 lo=base+q.start()-2;print('ref',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:lo-base+60],lo)))
for lo,hi in [(0x40002044,0x400020a0),(0x400daeb0,0x400daf40)]:
 print('WINDOW',hex(lo));print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:hi-base],lo)))
