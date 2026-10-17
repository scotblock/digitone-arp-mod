exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
out=[]
for m in re.finditer(rb'\x00\x00\x00\x00[\x01\x03\x04](?:z[PLRS]*|eh)?\x00',b):
 p=m.start()-4
 if p>=0:
  n=struct.unpack_from('>I',b,p)[0]
  if 8<=n<=256 and p+n+4<=len(b):out.append((hex(base+p),n,b[p:p+min(n+4,48)].hex()))
print('CIE candidates',out[:60], 'count',len(out))
# Raw references/PC-relative computations for known end records and global queue heads.
refs=[]
for m in re.finditer(b'\x41\x99',b):
 if m.start()+4<=len(b):
  v=struct.unpack_from('>I',b,m.start())[0]
  if 0x4199d400<=v<0x4199d594:refs.append((hex(base+m.start()),hex(v)))
pathlib.Path('work/lifetime-wide-ram-literals.json').write_text(__import__('json').dumps(refs,indent=2))
print('broader nearby literal refs',len(refs),'distinct', sorted(set(v for a,v in refs)))
