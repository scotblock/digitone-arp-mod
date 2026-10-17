exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
print('offset',hex(struct.unpack_from('>I',b,0x40174fc8-base-12)[0]))
for i in md.disasm(b[0x400a8dd2-base:0x400a8de0-base],0x400a8dd2):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
