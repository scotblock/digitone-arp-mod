exec(open('work/disassemble.py').read().split('out=[]')[0])
md.skipdata=True
out=[]
for s,e in [(0x40000400,0x40000620),(0x4009417e,0x400942ea),(0x40106b6c,0x40106de0),(0x40032816,0x400328a8),(0x400f0448,0x400f04c0)]:
 out.append(f'WINDOW {s:08x}')
 out.extend(f'{i.address:08x} {i.bytes.hex():20} {i.mnemonic:12} {i.op_str}' for i in md.disasm(b[s-base:e-base],s))
out.append('RAW ABSOLUTE REFERENCES: may include data; inspect boundaries')
for value in [0x4199fea0,0x4199fe98,0x48000000,0x40106db2,0x40106da2,0x401b107c,0x40200378,0x40106b6c]:
 needle=struct.pack('>I',value);p=0;hits=[]
 while True:
  p=b.find(needle,p)
  if p<0:break
  hits.append(f'{base+p:08x}');p+=1
 out.append(f'{value:08x}: '+','.join(hits))
out.append('05f8/05f7 operands in executable region: tentative decodes')
for value in [0x5f8,0x5f7]:
 needle=struct.pack('>H',value);p=0
 while True:
  p=b.find(needle,p,0x170000)
  if p<0:break
  if p%2==0 and p>=2:
   ins=list(md.disasm(b[p-2:p+12],base+p-2,count=1))
   if ins:out.append(f'{base+p:08x}: {ins[0].mnemonic} {ins[0].op_str}')
  p+=1
pathlib.Path('work/ownership-mapping.txt').write_text('\n'.join(out));print('\n'.join(out))
