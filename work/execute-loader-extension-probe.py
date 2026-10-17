"""Synthetic streams in RAM only: stock main depack caller, no firmware rebuild."""
exec(open('work/try-full-early-allocator.py').read().split('m=AllocMachine();')[0])
import json,hashlib
boot=pathlib.Path('work/section-2.bin').read_bytes();bootbase=0x02000800
RANGES.extend([(0x02000878,0x020009dc),(0x02000a58,0x02000aa0)])
def bootfetch(pc):
 if bootbase<=pc<bootbase+len(boot):return boot[pc-bootbase:pc-bootbase+16]
 return b[pc-base:pc-base+16]
loader_source=source.replace('b[pc-base:pc-base+16]','bootfetch(pc)')
loader_source=loader_source.replace('   self.steps.append(pc)',"   self.steps.append(pc)\n   if pc==0x020009d2:self.depacked_bytes=self.reg['d0']")
loader_source=loader_source.replace("('st','seq','sne','sge','scc')","('st','seq','sne','sge','scc','shi')").replace("'scc':not bool(self.sr&1)}","'scc':not bool(self.sr&1),'shi':not bool(self.sr&1) and not z}")
loader_source=loader_source.replace("   elif m=='swap':","   elif m=='movec':\n    self.controls.append({'pc':hex(pc),'selector':int.from_bytes(i.bytes[2:4],'big')&4095,'value':self.get(ops[0],4)})\n   elif m=='nop':pass\n   elif m=='swap':")
loader_source=loader_source.replace('range(100000)','range(500000)')
exec('if True:\n'+loader_source);plain_loader_run=run
summary_loader_source=loader_source.replace('   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)', '''   if pc==0x020009c2 and getattr(self,'summarize',False):
    assert bootfetch(pc)[:8]==bytes.fromhex('12da53826600fffa')
    count=self.reg['d2'];dst=self.reg['a1'];src=self.reg['a2'];off=dst-src;assert count>0 and off>0
    pattern=bytes(self.read(src+j,1) for j in range(min(off,count)))
    data=(pattern*((count+len(pattern)-1)//len(pattern)))[:count]
    self.bulk_write(dst,data);self.reg['a1']+=count;self.reg['a2']+=count;self.reg['d2']=0;self.flags(0,4,False,False,True)
    self.summaries.append({'bytes':count,'offset':off,'stock_loop_instructions':count*3});pc=0x020009ca;continue
   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)''')
summary_loader_source=summary_loader_source.replace('   if pc==0x020009c2', '''   if pc==0x02000890 and self.reg['d1']==0 and getattr(self,'literal_prefix',0)>0 and getattr(self,'summarize',False):
    count=self.literal_prefix;assert count%8==0;src=self.reg['a0'];dst=self.reg['a1'];data=bytearray()
    for j in range(count//8):
     assert self.read(src+j*9,1)==255
     data.extend(self.read(src+j*9+k,1) for k in range(1,9))
    self.bulk_write(dst,data);self.reg['a0']+=count//8*9;self.reg['a1']+=count;self.reg['d0']=1;self.reg['d1']=0xff80;self.reg['d2']=1;self.flags(data[-1],1)
    self.summaries.append({'literal_bytes':count,'tag_groups':count//8});self.literal_prefix=0;continue
   if pc==0x020009c2''')
exec('if True:\n'+summary_loader_source);summarized_loader_run=run
class LoaderMachine(Machine):
 def __init__(self,n):super().__init__();self.output=bytearray([0xa5])*(n+32);self.output_size=n;self.controls=[];self.summaries=[];self.summarize=False;self.output_write_count=0
 def read(self,a,n):
  if base<=a and a+n<=base+len(self.output):return int.from_bytes(self.output[a-base:a-base+n],'big')
  return super().read(a,n)
 def write(self,a,n,v):
  if base<=a and a+n<=base+len(self.output):self.output[a-base:a-base+n]=(v&((1<<(8*n))-1)).to_bytes(n,'big');self.output_write_count+=n;return
  return super().write(a,n,v)
 def bulk_write(self,a,data):
  assert base<=a and a+len(data)<=base+len(self.output);self.output[a-base:a-base+len(data)]=data;self.output_write_count+=len(data)
class Bits:
 def __init__(self):self.data=bytearray(8);self.remaining=0
 def bit(self,v):
  if not self.remaining:self.tag=len(self.data);self.data.append(0);self.remaining=8
  self.remaining-=1;self.data[self.tag]|=(v&1)<<self.remaining
 def byte(self,v):self.data.append(v)
 def gamma(self,v):
  for j in range(v.bit_length()-2,-1,-1):self.bit(v>>j&1);self.bit(j==0)
def stream(n,prefix=0):
 p=Bits()
 for j in range(prefix or 1):p.bit(1);p.byte(0x5a)
 remain=n-(prefix or 1);p.bit(0);p.gamma(2);p.bit(0);p.bit(0);p.gamma(remain-3)
 p.bit(0);p.gamma(0x1000002);p.byte(255)
 p.data[:4]=(len(p.data)-8).to_bytes(4,'big');p.data[4:8]=(sum(p.data[8:])&0xffffffff).to_bytes(4,'big')
 return bytes(p.data)
checks=[];cases=[]
def check(name,ok):assert ok,name;checks.append(name)
def execute(n,summarize,entry=0x02000a58,prefix=0):
 m=LoaderMachine(n);m.literal_prefix=prefix;m.sr=0x2700;m.map(0x30000000,0x4000);src=stream(n,prefix);m.map(0x40200000,len(src))
 for j,value in enumerate(src):m.write(0x40200000+j,1,value)
 guard=bytes(m.output[n:]);m.output_write_count=0
 m.summarize=summarize;m.run=(summarized_loader_run if summarize else plain_loader_run).__get__(m,LoaderMachine)
 result=m.run(entry,() if entry==0x02000a58 else (0x40200000,base))
 check(f'{n}/{summarize}: stock depacker returns actual output size',m.depacked_bytes==n)
 check(f'{n}/{summarize}: caller retains stock return-register behavior',result==0x8c000)
 check(f'{n}/{summarize}: decoded output exact',m.output[:n]==bytes([0x5a])*n)
 check(f'{n}/{summarize}: output guard untouched',m.output[n:]==guard)
 check(f'{n}/{summarize}: byte writes equal output size',m.output_write_count==n)
 check(f'{n}/{summarize}: stock control sequence preserved',[(x['selector'],hex(x['value'])) for x in m.controls]==[(2,'0xa508e000'),(4,'0x4003e000'),(5,'0xe020'),(4,'0x0'),(5,'0x0'),(2,'0x8c000')])
 cases.append({'decoded_bytes':n,'compressed_fixture_bytes':len(src),'executed_instructions':len(m.steps),'summarized_copies':m.summaries,'entry':hex(entry),'depacker_returned_bytes':m.depacked_bytes,'caller_d0':hex(result),'controls':m.controls})
 return m
plain=execute(4096,False);accelerated=execute(4096,True)
check('summary matches complete stock 4096-byte execution',plain.output==accelerated.output and plain.reg==accelerated.reg and plain.sr==accelerated.sr)
literal_plain=execute(8192,False,prefix=16);literal_fast=execute(8192,True,prefix=16)
check('literal summary matches full stock execution',literal_plain.output==literal_fast.output and literal_plain.reg==literal_fast.reg and literal_plain.sr==literal_fast.sr)
execute(len(b),True,prefix=0x50000);execute(len(b)+4096,True,prefix=0x50000)
# Original compressed stream reaches the source-address range used by the stock caller.
inspection=json.loads(pathlib.Path('work/inspection.json').read_text());sec=next(x for x in inspection['sections'] if x['id']==3)
check('original decoded output overlaps the compressed staging address range',base+len(b)>0x40200000)
r={'firmware_modified':False,'checks':checks,'cases':cases,'original_section':{'decoded_bytes':len(b),'compressed_bytes':sec['stored_bytes']},'proved':'Recovered section-2 main-depack caller accepts a valid synthetic stream with decoded size equal to stock plus 4096 bytes. No original-size rejection in the executed path.','not_proved':['device updater/container/flash acceptance','true extended-main compressed stream and source/output overlap behavior','external function 80005a88 that provides section descriptor','compressed staging/read limits for actual image','all alternate boot/handoff paths','hardware/cache execution'],'fixture':'Non-firmware repeated-byte compressed streams held only in PC memory; no patched, repacked or flashable image generated. Large backreference loops summarized after equality check against full 4096-byte execution.'}
pathlib.Path('outputs/Digitone-loader-extension-probe-results.json').write_text(json.dumps(r,indent=2))
print('PASS',len(checks),'checks; actual main depack caller handles stock+4096 decoded bytes; full updater acceptance remains unverified')
