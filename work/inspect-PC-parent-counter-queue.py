from pathlib import Path
exec(Path('work/inspect-PC-pattern-field-writers.py').read_text().split('for a,n')[0])
for a,n in [(0x4014a20a,240),(0x4002f80c,130),(0x400a87f0,246),(0x4002c1fe,120),(0x4001c900,110)]:
 print('WINDOW',hex(a))
 for i in c.disasm(d[a-b:a-b+n],a): print(hex(i.address),i.bytes.hex(),i.mnemonic,i.op_str)
for addr in [0x419f0d70,0x419f0d74]:
 needle=addr.to_bytes(4,'big');p=0;hits=[]
 while True:
  p=d.find(needle,p)
  if p<0:break
  hits.append(hex(b+p));p+=1
 print('COUNTER_LITERAL',hex(addr),len(hits),hits[:25])
