from pathlib import Path
import struct
b=Path('work/os144/section-3.bin').read_bytes();base=0x40000400
for a in [0x40100440,0x40240714,0x40240718,0x40240720,0x400e7eca,0x400c9536]:
 p=struct.pack('>I',a);idx=0;out=[]
 while True:
  idx=b.find(p,idx)
  if idx<0:break
  out.append(hex(base+idx));idx+=1
 print(hex(a),out)
for a in range(0x402406e0,0x40240740,4):print(hex(a),b[a-base:a-base+4].hex())
