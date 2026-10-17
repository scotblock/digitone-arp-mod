from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
print('VTABLE',[(hex(k),hex(int.from_bytes(d[0x40195bd8-b+k:0x40195bd8-b+k+4],'big'))) for k in range(0,0x70,4)])
for a,n in [(0x4014c0ce,110),(0x401530fe,116)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a):print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
for target in [0x40152ffe,0x40153060,0x40153078]:
 needle=target.to_bytes(4,'big');pos=0;refs=[]
 while True:
  pos=d.find(needle,pos)
  if pos<0:break
  refs.append(hex(b+pos));pos+=1
 print('REFS',hex(target),refs)
