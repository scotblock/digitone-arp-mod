from pathlib import Path
exec(Path('work/inspect-PC-copy-provenance.py').read_text().split('for a,n')[0]);c.skipdata=True
needle=(0x4002f80c).to_bytes(4,'big');pos=0
while True:
 pos=d.find(needle,pos)
 if pos<0:break
 print('REF',hex(b+pos))
 for i in c.disasm(d[pos-12:pos+10],b+pos-12):print(hex(i.address),i.mnemonic,i.op_str)
 pos+=1
