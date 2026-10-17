exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for t in [0x40008ac8,0x40008c5a,0x4000ae8e,0x4000b034,0x4000b19e,0x40013348]:
 cand=[]
 for o in range(t-base-1800,t-base,2):
  if b[o:o+2]==bytes.fromhex('4e56') or (b[o:o+3]==bytes.fromhex('4fefff') and b[o+4:o+6]==bytes.fromhex('48d7')):cand.append(base+o)
 print(hex(t),' '.join(hex(x) for x in cand[-5:]))
