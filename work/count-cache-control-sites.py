import pathlib,collections
b=pathlib.Path('work/section-3.bin').read_bytes();a=[]
for i in range(0,len(b)-1,2):
 w=int.from_bytes(b[i:i+2],'big')
 if w&0xff38==0xf428:a.append(0x40000400+i)
print(collections.Counter(hex(x&0xffff0000) for x in a));print([hex(x) for x in a if x<0x40200000])
