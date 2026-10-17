exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
print('CONFIG LITERAL CANDIDATES')
for pos in range(0,len(b)-4,2):
 v=struct.unpack_from('>I',b,pos)[0]
 if 0x4131b900<=v<0x4131ba80:
  print(f'{base+pos:08x} -> {v:08x}',b[max(pos-4,0):pos].hex())
print('APPLICATION +2B4 INSTRUCTION CANDIDATES')
for pos in range(0,0x180000,2):
 if b[pos:pos+2]==b'\x02\xb4':
  for back in (2,4):
   start=pos-back;i=next(md.disasm(b[start:start+16],base+start,count=1),None)
   if i and '$2b4(' in i.op_str: print(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}')
