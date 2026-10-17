exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for target in [0x401b4d81,0x401c3967,0x401c2f12]:
 print('STRINGREF',hex(target))
 for off in range(0,len(b)-6,2):
  if b[off+2:off+6]==struct.pack('>I',target):print(hex(base+off))
for start,end in [(0x4009c7c0,0x4009c838),(0x400dab8c,0x400dac48),(0x400dae20,0x400dae80),(0x4009bde8,0x4009be98)]:
 print('ENTRY',hex(start))
 for i in md.disasm(b[start-base:end-base],start):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
