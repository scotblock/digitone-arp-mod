exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for a in [0x401bb0ac,0x401bd1ce]:print(hex(a),b[a-base:].split(b'\0',1)[0])
for s,e in [(0x4006ed66,0x4006f1d0),(0x400d5d8e,0x400d5ec0)]:
 print('ENTRY',hex(s))
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic:12} {i.op_str}')
print('CONFIG OFFSET B6B8E0 CANDIDATES')
for pos in range(0,len(b)-4,2):
 if b[pos:pos+4]==bytes.fromhex('00b6b8e0'):print(hex(base+pos),b[max(pos-4,0):pos].hex())
