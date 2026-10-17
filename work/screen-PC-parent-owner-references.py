from pathlib import Path
exec(Path('work/screen-PC-pattern-owner-pointer-aliases.py').read_text().split('for base,packed')[0])
for target in [0x41a720a0,0x41a720d0]:
 hits=[]
 for base,packed in blob['pages'].items():
  data=zlib.decompress(packed);needle=target.to_bytes(4,'big');pos=0
  while True:
   pos=data.find(needle,pos)
   if pos<0:break
   if pos%2==0:hits.append(hex(base+pos))
   pos+=1
 print(hex(target),hits)
