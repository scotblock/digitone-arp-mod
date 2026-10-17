exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x40082660,0x40082740),(0x4006f8b0,0x4006fa40),(0x4006fb60,0x4006fc20),(0x4008fab0,0x4008fb50)]:
 print('WINDOW',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:12} {i.op_str}')
