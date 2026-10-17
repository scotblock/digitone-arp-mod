exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for vt in [0x401764c8,0x40173e14,0x40174d40]:
 print('VT',hex(vt))
 for off in [0x10,0x28,0x2c]:
  p=struct.unpack_from('>I',b,vt-base+off)[0];print(hex(off),hex(p))
  if 0x40000400<=p<0x40170000:
   for i in md.disasm(b[p-base:p-base+110],p):
    print(f'{i.address:08x} {i.bytes.hex():16} {i.mnemonic:10} {i.op_str}')
    if i.mnemonic=='rts':break
