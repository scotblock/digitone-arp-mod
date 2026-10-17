exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for start,end in [(0x4009f038,0x4009f0f4),(0x4009719e,0x40097220),(0x4009b600,0x4009b660),(0x4009e4a8,0x4009e4ee),(0x4009bd8a,0x4009bde8)]:
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
