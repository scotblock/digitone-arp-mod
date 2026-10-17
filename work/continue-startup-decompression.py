"""Continue startup through a checked stock decompressor loop summary. PC only."""
import pathlib,copy,json,hashlib,runpy
p=pathlib.Path('work/test-startup-completions.py').read_text()
exec(p.split("for mode in ['ready'")[0])
# Omit per-instruction timeline sampling outside the initializer; preserve stops,
# fixture events, allocator calls, and all initializer guard observations.
response_observe=s['observe_placed']
def fast_observe(m,pc):
 if pc in getattr(m,'startup_stops',[]):m.stop_pc=pc;raise t['Stop']()
 if pc in [0x400ec45c,0x400ece52,0x40000568,0x4009bcc4,0x400dab8c,0x400ec284,0x4000054c,t['n']['SPIN']] or 0x400f0504<=pc<0x400f05d6 or getattr(m,'code_start',0)<=pc<getattr(m,'code_end',0):response_observe(m,pc)
s['observe_placed']=fast_observe
exec(p[p.index('# Resume full'):p.index('constructor_state=m;')])
constructor=m;owner_before=t['protected'](m,owner)
dec=runpy.run_path('work/validate-startup-decompression.py')['decode_asset']
results={'checks':checks,'cases':cases,'firmware_modified':False}
# Cache instruction decoding only; no changed instruction semantics.
class CachedMD:
 def __init__(self,real):self.real=real;self.cache={}
 def disasm(self,data,pc,count=0):
  key=(pc,bytes(data))
  if key not in self.cache:self.cache[key]=list(self.real.disasm(data,pc,count=count))
  return iter(self.cache[key])
s['md']=CachedMD(s['md'])
# First actual match boundary, used to verify the exact loop summary.
m.configure(uart='current_version');m.stock_flash=True;m.timer_complete=True;m.startup_stops=[0x400ee404];s['active']=m
try:m.advance(0x4008c7f4)
except t['Stop']:pass
initial=m
print('first match',m.reg,flush=True)
plain=s['advance']

def copy_match(m):
 count=m.reg['d2']+1;srca=m.reg['a2'];dst=m.reg['a1']
 assert 0<count<=0x800000
 for j in range(count):m.write(dst+j,1,m.read(srca+j,1))
 m.reg['a1']+=count;m.reg['a2']+=count;m.reg['d2']=0;m.flags(0,4,False,False,True)
 m.match_summaries=getattr(m,'match_summaries',0)+1
s['copy_match']=copy_match
fastsrc=advance_src.replace('range(2000000)','range(8000000)').replace("   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)","   if pc==0x400ee404 and getattr(self,'fast_matches',False):\n    copy_match(self);pc=0x400ee40e;continue\n   assert any(lo<=pc<hi for lo,hi in RANGES),hex(pc)")
exec('if True:\n'+fastsrc,s);fast=s['advance']
for count,distance in [(2,1),(7,1),(7,3),(7,20),(100,31)]:
 states=[]
 for usefast in [False,True]:
  q=copy.deepcopy(initial);s['active']=q;q.reg['a1']=0x40509000;q.reg['a2']=q.reg['a1']-distance;q.reg['d2']=count-1;q.fast_matches=usefast;q.startup_stops=[0x400ee40e]
  for j in range(128):q.write(0x40508f80+j,1,j&255)
  q.advance=(fast if usefast else plain).__get__(q,ResponseMachine)
  try:q.advance(0x400ee404)
  except t['Stop']:pass
  states.append((q.reg,q.sr,bytes(q.read(0x40508f80+j,1) for j in range(256))))
 check(f'match summary equals stock loop count {count} distance {distance}',states[0]==states[1])
# Resume at the real first-match boundary, retain bit/offset decoding in stock.
m=initial;m.fast_matches=True;m.startup_stops=[0x400ee416];s['active']=m;m.advance=fast.__get__(m,ResponseMachine);before=len(m.steps)
try:m.advance(0x400ee404)
except t['Stop']:pass
except Exception as e:
 print('decomp failed',repr(e),hex(m.steps[-1]),m.reg,flush=True);raise
source=m.read(m.reg['a7']+0x18,4) # after stock prologue, args +24
# d4 is original output base, a1 current output end at stock return calculation.
destination=m.reg['d4'];size=m.reg['a1']-destination
blob=b[source-base:];expected,info,tokens=dec(blob)
actual=bytes(m.read(destination+j,1) for j in range(size))
check('stock output matches independent decoder byte for byte',actual==expected)
check('stock return size matches independent decoder',m.reg['d0']==len(expected))
check('stock input cursor consumes advertised compressed byte count',m.reg['a0']-source-8==info['compressed_size'])
check('decompression preserves owner and allocation',t['protected'](m,owner)==owner_before)
results['decompression']={'source':hex(source),'destination':hex(destination),'end':hex(destination+size),'stock_return_size':size,'stock_instructions_after_first_match':len(m.steps)-before,'summarized_matches':m.match_summaries,**info}
print('decompressed',results['decompression'],flush=True)
# Resume stock epilogue and caller, with a boundary just before initializer.
m.startup_stops=[0x400f0504];before=len(m.steps);outcome=None
try:m.advance(0x400ee416)
except t['Stop']:outcome='initializer reached'
except Exception as e:outcome=f'{type(e).__name__}: {e}'
check('remaining executed startup preserves owner and allocation',t['protected'](m,owner)==owner_before)
results['continuation']={'outcome':outcome,'last_pc':hex(m.steps[-1]),'instructions':len(m.steps)-before,'regs':m.reg.copy()}
# Record provenance diagnostics for the next bounded continuation audit.
results['continuation']['last_instructions']=[hex(pc) for pc in m.steps[-80:]]
results['continuation']['stack_words']=[(hex(m.reg['a7']+j),hex(m.read(m.reg['a7']+j,4))) for j in range(0,96,4)]
results['continuation']['argument_recent_writes']=[(hex(a),z,hex(v)) for a,z,v in m.writes if 0x30001f60<=a<0x30001f88][-80:]
if outcome=='initializer reached':
 m.startup_stops=[0x4009bcc4];before=len(m.steps);init_outcome=None
 code_before=bytes(m.read(m.code_start+j,1) for j in range(4096))
 try:m.advance(0x400f0504)
 except t['Stop']:init_outcome='stock caller return boundary reached'
 except Exception as e:init_outcome=f'{type(e).__name__}: {e}'
 check('initializer preserves allocated owner pointer',m.read(0x4199d590,4)==owner)
 check('initializer preserves executable code bytes',bytes(m.read(m.code_start+j,1) for j in range(4096))==code_before)
 if init_outcome=='stock caller return boundary reached':
  check('initializer publishes ready only after stock return',m.read(owner+0x1410c,4)==1)
  check('initializer clears retained contexts',all(m.read(owner+0x14120+j,1)==0 for j in range(0xb50)))
 results['initializer']={'outcome':init_outcome,'last_pc':hex(m.steps[-1]),'instructions':len(m.steps)-before,'owner':hex(m.read(0x4199d590,4)),'ready':m.read(owner+0x1410c,4)}
check('original decoded firmware unchanged',hashlib.sha256(pathlib.Path('work/section-3.bin').read_bytes()).hexdigest()=='ba336089d28edc7631df14b12c4a93f8a3c9186a0de8859797a6a3ad05e297f6')
check('original SysEx unchanged',hashlib.sha256(syx).hexdigest()=='0de87bf55e6bc48bebef5479e0d054f262fb7a0c7f81052dbd195d38569fdfda')
results['check_count']=len(checks)
pathlib.Path('outputs/Digitone-startup-decompression-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'checks':len(checks),'continuation':results['continuation']},indent=2),flush=True)
