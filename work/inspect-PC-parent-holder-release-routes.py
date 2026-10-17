from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for target in [0x419f0de4,0x40149ab8]:
 needle=target.to_bytes(4,'big');pos=0;refs=[]
 while True:
  pos=d.find(needle,pos)
  if pos<0:break
  refs.append(hex(b+pos))
  if target==0x419f0de4:
   for i in c.disasm(d[pos-2:pos+8],b+pos-2):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
  pos+=1
 print('WORDS',hex(target),refs)
for i in c.disasm(d[0x40149ab8-b:0x40149ad2-b],0x40149ab8):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
