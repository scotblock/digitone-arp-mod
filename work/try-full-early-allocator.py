exec(open('work/execute-full-handler-transition.py').read().split('checks=[];cases=[]')[0])
source=source.replace("'bpl','bmi','blt')", "'bpl','bmi','blt','bls','bhi')").replace("'blt':negative}","'blt':negative,'bls':bool(self.sr&1) or z,'bhi':not bool(self.sr&1) and not z}")
source=source.replace("   elif m=='btst':", "   elif m in ('bset','bclr','bchg'):\n    width=4 if ops[1] in self.reg else 1;bit=self.get(ops[0],4)%(width*8);value=self.get(ops[1],width);self.sr=(self.sr&~4)|(0 if value&(1<<bit) else 4);self.put(ops[1],width,value|(1<<bit) if m=='bset' else value&~(1<<bit) if m=='bclr' else value^(1<<bit))\n   elif m=='btst':")
exec('if True:\n'+source);Machine.run=run
RANGES.extend([(0x400da9a4,0x400dae08),(0x40001a4c,0x40001ae0),(0x40001b6e,0x40001be0)])
class AllocMachine(Machine):
 def read(self,a,n):
  if any(lo<=a and a+n<=hi for lo,hi in [(0x41925eb8,0x41945ed8),(0x419a38c0,0x429a39a8),(0x429a39a8,0x429a39ac)]):return int.from_bytes(bytes(self.mem.get(a+j,0) for j in range(n)),'big')
  return super().read(a,n)
 def write(self,a,n,v):
  if any(lo<=a and a+n<=hi for lo,hi in [(0x41925eb8,0x41945ed8),(0x419a38c0,0x429a39a8),(0x429a39a8,0x429a39ac)]):
   for j,x in enumerate((v&((1<<(8*n))-1)).to_bytes(n,'big')):self.mem[a+j]=x
   self.writes.append((a,n,v&((1<<(8*n))-1)));return
  return super().write(a,n,v)
m=AllocMachine();m.map(0x30000000,0x4000);m.map(0x401fe590,0x20)
for j in range(0x20):m.write(0x401fe590+j,1,b[0x401fe590-base+j])
print('result',hex(m.run(0x400dab8c,(0x15c80,))),'steps',len(m.steps))
