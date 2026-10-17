from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for target in [0x419f0de0,0x40152a1c,0x40152bae]:
 needle=target.to_bytes(4,'big');pos=0;refs=[]
 while True:
  pos=d.find(needle,pos)
  if pos<0:break
  refs.append(hex(b+pos))
  if target==0x419f0de0:
   print('REF',hex(b+pos))
   for i in c.disasm(d[pos-12:pos+18],b+pos-12):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
  pos+=1
 print('WORDS',hex(target),refs)
