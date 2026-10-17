exec(open('work/receiver-route-refs.py').read().split('for a in [')[0])
for a in [0x419950a4,0x400ed8ea,0x400eb524,0x400ed8dc,0x419eaf08,0x419cf750]:
 i=0;out=[];p=struct.pack('>I',a)
 while True:
  i=b.find(p,i)
  if i<0:break
  out.append(hex(base+i));i+=1
 print(hex(a),out)
