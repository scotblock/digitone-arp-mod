"""Differential machine-code checks and existing copy/producer ABI cases."""
import pathlib,sys,json,struct,random,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn.m68k_const import *
BASE,PTR,BSS,STACK=0x47be0000,0x47be1000,0x47be1004,0x47fdff00
POOL,CACHE,PATTERN=0x4199da94,0x419a304c,0x47bc0000
info=json.loads(pathlib.Path('work/packed-context-build.json').read_text())
old_layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())
old_build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
old_layout.update(slot={'address':old_build['slot_address']})
new_layout=info['layout'];machines=[]
regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
for name in ['cache-context-overlay','packed-context-overlay']:
 m=Machine(ddr=0x08000000)
 for a in [BASE,STACK,POOL,PATTERN,0x41344000,0x47bccf04]:m.ensure(a)
 blob=pathlib.Path('work/'+name+'.bin').read_bytes();m.uc.mem_write(BASE,blob)
 if name.startswith('packed'):m.install_isa_patches_scoped(blob[:info['code_bytes']],BASE)
 else:m.install_isa_patches_scoped(blob[:1892],BASE);m.install_isa_patches_scoped(blob[2368:],BASE+2368)
 machines.append(m)
u32=lambda v:struct.pack('>I',v&0xffffffff)
counts={};rng=random.Random(54418)
def compare(name,args,state=None,d0=None):
 results=[]
 for idx,m in enumerate(machines):
  uc=m.uc;uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
  for a in [POOL,CACHE,PATTERN,0x41344530,0x41345f08,0x41345620]:uc.mem_write(a,bytes(4096))
  if state:
   for a,b in state.items():uc.mem_write(a,b)
  for j,r in enumerate(regs):uc.reg_write(r,0x11223000+j*0x100)
  uc.reg_write(UC_M68K_REG_SR,0x2700)
  if d0 is not None:uc.reg_write(UC_M68K_REG_D0,d0)
  layout=[old_layout,new_layout][idx]
  call(m,layout[name]['address'],args,stack_top=STACK,limit=100000)
  assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0,(name,args)
  values=[uc.reg_read(r) for r in regs]
  # Only relocated internal code/table addresses may differ in scratch registers.
  if idx==0:
   for j,v in enumerate(values):
    if 0x47be0770<=v<0x47be0770+420:values[j]=info['table_address']+v-0x47be0770
  uc.mem_write(STACK-0x200,bytes.fromhex('40c7'));uc.emu_start(STACK-0x200,STACK-0x1fe,count=1)
  results.append((values,uc.reg_read(UC_M68K_REG_D7)&0xffff,bytes(uc.mem_read(PTR,0xb74)),bytes(uc.mem_read(POOL,4096)),bytes(uc.mem_read(CACHE,4096))))
 assert results[0]==results[1],(name,args,d0,[(r[0],r[1]) for r in results])
 counts[name]=counts.get(name,0)+1
for track in [0,1,2,3,4,127,0xffffffff]:
 for bad in range(-1,5):
  state={}
  if bad==4:state[PTR]=u32(0)
  elif bad>=0:state[BSS+bad*4]=u32([0x534c4332,2,0xb70,1][bad]^1)
  compare('resolve',[],state,track)
for origin,limit in [(POOL,9216),(CACHE,288)]:
 for offset in range(-1,limit+1):compare('slot',[],d0=origin+offset)
for bad in [0,1,2,3,4,5]:
 for track in range(4):
  identity=0x419c38c0+track*0x504;record=BSS+0xb30+track*16
  fields=[identity,0x800000bd|(track<<13),bad if bad<3 else 0,0x80000000|track]
  if bad==3:fields[0]^=4
  if bad==4:fields[3]^=1
  if bad==5:fields[1]=0
  state={record:struct.pack('>IIII',*fields)}
  compare('read',[record,identity,track],state)
  compare('begin',[record],state);compare('cancel',[record],state)
  for word in [0,0x800000bd|(track<<13),0x7fffffff,0x8000123b,0xffffffff]:compare('commit',[record,identity,word,track],state)
for event in [POOL+i*72 for i in range(128)]+[CACHE+i*72 for i in range(4)]+[POOL-1,POOL+1,CACHE-1,CACHE+288]:
 for bad in [-1,0,1,2,3,4]:
  state={BSS+32:bytes((i*7)&255 for i in range(512)),BSS+2592:bytes(range(16))}
  if bad==4:state[PTR]=u32(0)
  elif bad>=0:state[BSS+bad*4]=u32([0x534c4332,2,0xb70,1][bad]^1)
  compare('candidate_store',[event,0x8000433b],state)
  if bad==-1:compare('snapshot',[event],state)
for track in [0,1,2,3,4,0xffffffff]:
 for root in [0,61,127,128,255]:
  for raw in [-128,-2,-1,0,5,34,35,127]:
   state={}
   if track<4:state[PATTERN+track*0x3d0+0x3cb]=bytes([root]);state[PATTERN+track*0x3d0+0x3ce]=bytes([raw&255])
   compare('capture',[PATTERN,track],state)
for _ in range(2500):
 note=rng.choice([0,1,57,127,128,0xffffffff,rng.randrange(128)])
 word=rng.choice([rng.getrandbits(32),0x80000000|rng.randrange(128)|(rng.randrange(37)<<7)|(rng.randrange(4)<<13)])
 compare('quantize',[note,word])
for track in range(4):
 identity=0x419c38c0+track*0x504;record=BSS+0xb30+track*16;event=POOL+track*72
 for bad in range(-1,19):
  e=bytearray(72)
  for off,v in [(0,0),(4,1),(8,track),(40,1<<19),(64,identity)]:e[off:off+4]=u32(v)
  cached=bytearray(e);state={event:bytes(e),0x41345f08+track*72:bytes(cached),0x41344530+track*40+24:u32(identity),0x41345620+track*4:u32(1),record:struct.pack('>IIII',identity,0x8000433b|(track<<13),0,0x80000000|track)}
  changes={0:(event,2),1:(event+4,0),2:(event+8,4),3:(event+40,0),4:(event+64,0),5:(0x41344530+track*40+24,identity+4),6:(0x41345620+track*4,0),7:(0x41345f08+track*72,2),8:(0x41345f08+track*72+4,0),9:(0x41345f08+track*72+8,track^1),10:(0x41345f08+track*72+64,identity+4),11:(0x41345f08+track*72+40,0),12:(PTR,0),13:(BSS,0),14:(BSS+4,0),15:(BSS+8,0),16:(BSS+12,0),17:(record+8,1),18:(record+12,0)}
  if bad>=0:a,v=changes[bad];state[a]=u32(v)
  compare('pitch',[event,57],state)
result={'passed':True,'firmware_modified':False,'differential_cases':counts,'registers_materialized_SR_storage_events_equal':True,'table_scratch_pointer_relocation_normalized':True,'build_sha256':info['sha256']}
pathlib.Path('outputs/Digitone-packed-context-differential-checks.json').write_text(json.dumps(result,indent=2));print('PASS differential',counts,flush=True)
# Reuse the existing stock memcpy / cache producer tests, with separate outputs.
source=pathlib.Path('work/test-cache-context-helpers.py').read_text()
source=source.replace("json.loads(pathlib.Path('work/native-overlay-layout.json').read_text())","info['layout']")
source=source.replace("json.loads(pathlib.Path('work/cache-context-build.json').read_text())","dict(slot_address=info['layout']['slot']['address'],copy_address=info['layout']['copy']['address'],first_copy_address=info['layout']['first_copy']['address'],hooks=[0x4009344e,0x40093892])")
source=source.replace('work/cache-context-overlay.bin','work/packed-context-overlay.bin').replace('Digitone-cache-context-helper-checks.json','Digitone-packed-context-copy-checks.json')
source=source.replace('m.install_isa_patches_scoped(blob,RAM)',"m.install_isa_patches_scoped(blob[:info['code_bytes']],RAM)")
exec(compile(source,'packed-context-existing-copy-tests','exec'))
