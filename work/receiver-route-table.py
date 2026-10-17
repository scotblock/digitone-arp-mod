exec(open('work/receiver-route-refs.py').read().split('for a in [')[0])
for a in [0x40240084,0x401ce294,0x400eaac8,0x400e8440]:
 p=struct.pack('>I',a);i=0;o=[]
 while True:
  i=b.find(p,i)
  if i<0:break
  o.append(hex(base+i));i+=1
 print(hex(a),o)
for a in [0x40240084,0x401ce1ea,0x401ce294]:print(hex(a),b[a-base:a-base+80].hex())
