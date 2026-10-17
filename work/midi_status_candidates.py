exec(open('work/disassemble.py').read().split('out=[]')[0])
for pat in ['00000090','00000080','000000b0','000000f0']:
 vals=[]
 for m in re.finditer(bytes.fromhex(pat),b[:0x170000]):
  o=m.start();prefix=b[max(0,o-4):o].hex()
  if prefix.endswith('0c80') or prefix.endswith('0c81') or prefix.endswith('0c82') or prefix.endswith('0c83') or prefix.endswith('0c84') or prefix.endswith('0c85') or prefix.endswith('0c86') or prefix.endswith('0c87'):vals.append(hex(base+o-2))
 print(pat,vals)
