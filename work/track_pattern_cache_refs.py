exec(open('work/disassemble.py').read().split('out=[]')[0])
for target in [0x419a302c,0x419a304c,0x413421b4]:
 print(f'REFS {target:08x}',[hex(base+m.start()) for m in re.finditer(re.escape(struct.pack('>I',target)),b)])
