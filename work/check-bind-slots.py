import pathlib,struct
b=pathlib.Path('work/section-3.bin').read_bytes();base=0x40000400
for vt in [0x40174d40,0x40173e14]:
 p=struct.unpack_from('>I',b,vt-base+0x24)[0]
 print(f'{vt:08x} slot +24 = {p:08x}')
