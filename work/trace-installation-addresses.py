exec(open('work/disassemble.py').read().split('out=[]')[0])
for value in [0x431dc690,0x431dc6a0,0x48000000,0x400dab8c,0x40241c94]:
 pat=value.to_bytes(4,'big');p=0;hits=[]
 while True:
  p=b.find(pat,p)
  if p<0:break
  hits.append(hex(base+p));p+=1
 print(hex(value),hits)
 for h in hits[:12]:
  lo=int(h,16)-6
  print('\n'.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b[lo-base:lo-base+40],lo)))
print('tailbeforepadding',b[0x40241c40-base:0x40241ca0-base].hex())
