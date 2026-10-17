exec(open('work/disassemble.py').read().split('out=[]')[0]);md.skipdata=True
for s,e in [(0x400165d0,0x400165dc),(0x400d75f4,0x400d75fe)]:
 for i in md.disasm(b[s-base:e-base],s):print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
