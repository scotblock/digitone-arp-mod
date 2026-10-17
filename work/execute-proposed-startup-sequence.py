"""PC-only split-clear sequence; large clear loops use validated summaries."""
exec(open('work/test-early-allocator-and-source-copy.py').read().split('checks=[];cases=[]')[0])
clearlo,clearhi=0x40242000,0x431dc690;stage=base+len(b);stageend=stage+4096
fixtures={};loop_pcs={}
for j,(lo,hi) in enumerate([(clearlo,stage),(stageend,clearhi),(0x29000000,0x29000110)]):
 code=bytearray(b[0x400004b2-base:0x400004e8-base]);code[10:14]=lo.to_bytes(4,'big');code[16:20]=hi.to_bytes(4,'big')
 addr=0x50030000+j*0x100;fixtures[addr]=bytes(code);loop_pcs[addr+0x20]=addr+0x2c
 RANGES.append((addr,addr+len(code)))
def seqfetch(pc):
 for addr,code in fixtures.items():
  if addr<=pc<addr+len(code):return code[pc-addr:pc-addr+16]
 return b[pc-base:pc-base+16]
seqsource=source.replace('b[pc-base:pc-base+16]','seqfetch(pc)')
exec('if True:\n'+seqsource);AllocMachine.run=run
summarysource=seqsource.replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)', '''   if pc in loop_pcs and getattr(self,'summarize',False):
    assert seqfetch(pc)[:12]==bytes.fromhex('48d000f041e80010538166f4')
    assert all(self.reg[r]==0 for r in ['d4','d5','d6','d7'])
    count=self.reg['d1'];lo=self.reg['a0'];hi=lo+16*count;assert count>0
    self.zero_range(lo,hi);self.reg['a0']=hi;self.reg['d1']=0;self.flags(0,4,False,False,True)
    self.summaries.append({'start':hex(lo),'end_exclusive':hex(hi),'iterations':count,'stock_loop_instructions':count*4});pc=loop_pcs[pc];continue
   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)''')
exec('if True:\n'+summarysource);summarized_run=run
class SequenceMachine(AllocMachine):
 def __init__(self):super().__init__();self.summarize=False;self.summaries=[]
 def read(self,a,n):
  if clearlo<=a and a+n<=clearhi:return int.from_bytes(bytes(self.mem.get(a+j,0) for j in range(n)),'big')
  return super().read(a,n)
 def write(self,a,n,v):
  if clearlo<=a and a+n<=clearhi:
   for j,x in enumerate((v&((1<<(8*n))-1)).to_bytes(n,'big')):
    if x:self.mem[a+j]=x
    else:self.mem.pop(a+j,None)
   self.writes.append((a,n,v&((1<<(8*n))-1)));return
  return super().write(a,n,v)
 def zero_range(self,lo,hi):
  assert clearlo<=lo<hi<=clearhi or 0x29000000<=lo<hi<=0x29000110
  for a in list(self.mem):
   if lo<=a<hi:
    if clearlo<=a<clearhi:self.mem.pop(a)
    else:self.mem[a]=0
  self.writes.append((lo,hi-lo,0))
checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
# Independently compare the actual small clear body with its summary.
for use_summary in [False,True]:
 m=SequenceMachine();m.sr=0x2700;m.map(0x30000000,0x4000);m.map(0x29000000,0x120)
 for j in range(0x120):m.write(0x29000000+j,1,0x55)
 m.summarize=use_summary;m.run=summarized_run.__get__(m,SequenceMachine) if use_summary else AllocMachine.run.__get__(m,SequenceMachine)
 m.run(0x50030200);state=(m.reg.copy(),m.sr,bytes(m.read(0x29000000+j,1) for j in range(0x120)))
 if use_summary:check('summarized clear equals 17 fully executed iterations',state==plain_state)
 else:plain_state=state
for exhausted in [False,True]:
 m=SequenceMachine();m.run=summarized_run.__get__(m,SequenceMachine);m.summarize=True;m.sr=0x2700;m.map(0x30000000,0x4000);m.map(0x401fe590,0x20)
 for j in range(0x20):m.write(0x401fe590+j,1,b[0x401fe590-base+j])
 for a in range(clearlo,clearhi,4096):m.write(a,1,0x99)
 for a in [clearlo,stage-1,stageend,clearhi-1,0x429a39a8,0x41945ebc]:m.write(a,1,0x77)
 payload=bytes((j*73+19)&255 for j in range(4096))
 for j,v in enumerate(payload):m.write(stage+j,1,v)
 m.run(0x50030000);m.run(0x50030100)
 check(f'{exhausted}: source survives both clears',bytes(m.read(stage+j,1) for j in range(4096))==payload)
 check(f'{exhausted}: every represented BSS byte outside source cleared',all(not(clearlo<=a<clearhi) or stage<=a<stageend or value==0 for a,value in m.mem.items()))
 if exhausted:check('pressure case occupies entire heap using stock allocator',m.run(0x400dab8c,(0x1000000,))==heaplo)
 owner=m.run(0x400dab8c,(0x15c80,));dest=owner+0x14c80 if owner else None
 if owner:
  m.run(0x400ec284,(owner,0,0x15c80));m.run(0x400ec23c,(dest,stage,4096))
  check('success: source fully copied into actual allocation',bytes(m.read(dest+j,1) for j in range(4096))==payload)
 else:check('pressure: actual null return bypasses copying',owner==0)
 before_erase={a:v for a,v in m.mem.items() if clearlo<=a<clearhi and not(stage<=a<stageend) and v}
 m.run(0x400ec284,(stage,0,4096))
 check(f'{exhausted}: staging restores stock zero contract',all(m.read(stage+j,1)==0 for j in range(4096)))
 check(f'{exhausted}: source erase preserves all other BSS state',{a:v for a,v in m.mem.items() if clearlo<=a<clearhi and v}==before_erase)
 check(f'{exhausted}: owner remains unpublished',m.read(0x4199d590,4)==0)
 check(f'{exhausted}: no scheduler trap taken',not any(pc in m.steps for pc in [0x40001a9e,0x40001bcc]))
 check(f'{exhausted}: interrupts remain masked',m.sr&0xff00==0x2700)
 cases.append({'exhausted':exhausted,'owner':hex(owner),'destination':None if dest is None else hex(dest),'executed_instructions':len(m.steps),'summarized_clears':m.summaries,'publication':'disabled: relocation and validation not implemented','continuation':'stopped before stock cache/hardware setup; failure continuation remains unverified'})
result={'checks':checks,'cases':cases,'firmware_modified':False,'scope':'PC driver executes proposed split-clear clones and unchanged stock allocation/clear/copy routines. Sparse whole-BSS memory; millions of repetitive clear iterations summarized, checked against 17 full iterations. No installed hook, hardware registers, relocation, or publication.'}
pathlib.Path('outputs/Digitone-proposed-startup-sequence-results.json').write_text(json.dumps(result,indent=2))
print('PASS',len(checks),'checks; success and actual heap-pressure/null paths; firmware unchanged')
