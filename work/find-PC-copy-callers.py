from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0])
c.skipdata=True
for a in [0x4000a1a6,0x4018ab1a]:
 needle=b'\x4e\xb9'+a.to_bytes(4,'big');pos=0
 while True:
  pos=d.find(needle,pos)
  if pos<0:break
  pc=b+pos;print('CALL',hex(a),hex(pc))
  for i in c.disasm(d[pos-36:pos+12],pc-36):print(hex(i.address),i.mnemonic,i.op_str)
  pos+=1
