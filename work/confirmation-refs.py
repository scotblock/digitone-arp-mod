exec(open('work/receiver-route-refs.py').read().split('for a in [')[0])
for a in [0x400eb570,0x400eb562,0x40001d6c,0x400c9cca,0x4014a20a,0x40161dda]:
 p=struct.pack('>I',a);i=0;o=[]
 while True:
  i=b.find(p,i)
  if i<0:break
  o.append(hex(base+i));i+=1
 print(hex(a),o)
