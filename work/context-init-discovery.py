exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x400f0504,0x400f05d6),(0x4009bcb8,0x4009bd8a),(0x4009bde8,0x4009be5c),(0x400f08f0,0x400f0956),(0x400ec284,0x400ec2ce),(0x400ef9d0,0x400efa20)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
