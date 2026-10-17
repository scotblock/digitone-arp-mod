"""Differential context commit, begin/cancel continuations and allocator return."""
import pathlib,json,struct,sys
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from unicorn.m68k_const import *
BASE,PTR,BSS,POOL,STACK=0x47be0000,0x47be1000,0x47be1004,0x4199da94,0x47fdff00
info=json.loads(pathlib.Path('work/packed-context-build.json').read_text())
layouts=[json.loads(pathlib.Path('work/native-overlay-layout.json').read_text()),info['layout']]
machines=[];regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
for idx,name in enumerate(['cache-context-overlay','packed-context-overlay']):
 m=Machine(ddr=0x08000000)
 for a in [BASE,STACK,POOL,POOL+9216,0x47bccf04,0x4009de50,0x4009719e,0xdeadbee0]:m.ensure(a)
 blob=pathlib.Path('work/'+name+'.bin').read_bytes();m.uc.mem_write(BASE,blob)
 m.install_isa_patches_scoped(blob[:info['code_bytes'] if idx else 1892],BASE)
 if not idx:m.install_isa_patches_scoped(blob[2368:],BASE+2368)
 machines.append(m)
def u32(v):return struct.pack('>I',v&0xffffffff)
def observed(m):
 values=[m.uc.reg_read(r) for r in regs];m.uc.mem_write(STACK-0x200,bytes.fromhex('40c7'));m.uc.emu_start(STACK-0x200,STACK-0x1fe,count=1)
 return values+[m.uc.reg_read(UC_M68K_REG_D7)&0xffff]
def setup(m,track,event,word,busy=1):
 uc=m.uc;identity=0x419c38c0+track*0x504
 uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
 uc.mem_write(event,bytes(72));uc.mem_write(event+8,u32(track));uc.mem_write(event+64,u32(identity))
 if 0<=event-POOL<9216 and (event-POOL)%72==0:uc.mem_write(BSS+32+(event-POOL)//72*4,u32(word))
 uc.mem_write(BSS+0xb30+track*16,struct.pack('>IIII',identity,word,busy,0))
 for j,r in enumerate(regs):uc.reg_write(r,0x24680100+j)
 uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A3,event);uc.reg_write(UC_M68K_REG_A7,STACK)
cases=0
for track in range(4):
 for index in [0,1,64,127,128]:
  for valid in [False,True]:
   event=POOL+index*72;results=[]
   for idx,m in enumerate(machines):
    setup(m,track,event,(0x800000bd|(track<<13)) if valid else 0)
    m.uc.emu_start(layouts[idx]['caller_commit']['address'],0x4009de50,count=10000)
    assert m.uc.reg_read(UC_M68K_REG_PC)==0x4009de50
    results.append((observed(m),bytes(m.uc.mem_read(BSS,0xb70)),bytes(m.uc.mem_read(event,72))))
   assert results[0]==results[1],(track,index,valid);cases+=1
allocator_cases=0
for event in [0,POOL,POOL+72,POOL+127*72,POOL+128*72,POOL+1,0x419a304c,0x419a304c+288]:
 results=[]
 for idx,m in enumerate(machines):
  setup(m,0,POOL,0x800000bd);m.uc.reg_write(UC_M68K_REG_A0,event);m.uc.mem_write(STACK,u32(0xdeadbee0))
  pc=0x47be063c if not idx else info['instruction_map'][str(0x47be063c)]
  m.uc.emu_start(pc,0xdeadbee0,count=10000);assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
  results.append((observed(m),bytes(m.uc.mem_read(BSS,0xb70))))
 assert results[0]==results[1],event;allocator_cases+=1
before_after_cases=0
for name,end in [('before',0x4009719e),('after',0x4009ddac)]:
 for track in [0,1,2,3,4]:
  for saved_result in [0,1]:
   results=[]
   for idx,m in enumerate(machines):
    m.ensure(end);setup(m,min(track,3),POOL,0x800000bd)
    m.uc.reg_write(UC_M68K_REG_D0,saved_result)
    m.uc.mem_write(STACK,u32(track if name=='after' else 0x12345678)+u32(track))
    m.uc.emu_start(layouts[idx][name]['address'],end,count=10000);assert m.uc.reg_read(UC_M68K_REG_PC)==end
    top=bytes(m.uc.mem_read(STACK,8))
    if name=='before':assert top[:4]==u32(layouts[idx]['after']['address']);top=b'CODE'+top[4:]
    results.append((observed(m),bytes(m.uc.mem_read(BSS,0xb70)),top))
   assert results[0]==results[1],(name,track,saved_result);before_after_cases+=1
out={'passed':True,'firmware_modified':False,'commit_ABI_cases':cases,'allocator_return_ABI_cases':allocator_cases,'before_after_continuation_ABI_cases':before_after_cases,'registers_materialized_SR_storage_and_event_match':True,'before_return_continuation_correctly_relocated':True}
pathlib.Path('outputs/Digitone-packed-context-outer-ABI.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
