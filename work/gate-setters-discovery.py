exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x4002aeee,0x4002af72),(0x4002b31a,0x4002b3f0),(0x4002c7e0,0x4002c884),(0x401382dc,0x4013835e)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
