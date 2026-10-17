"""Commit trampoline differential ABI across valid and invalid event slots."""
import pathlib,json,struct
exec(pathlib.Path('work/test-indexed-context-lookup.py').read_text().split('started=time.monotonic()')[0])
regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
def observed(m):
 values=[m.uc.reg_read(r) for r in regs]
 m.uc.mem_write(0x47fdfd00,bytes.fromhex('40c7'));m.uc.emu_start(0x47fdfd00,0x47fdfd02,count=1)
 return values+[m.uc.reg_read(UC_M68K_REG_D7)&0xffff]
cases=[]
for track in range(4):
 for index in [0,1,64,127,128]:
  for valid in [False,True]:
   event=POOL+index*72;identity=0x419c38c0+track*0x504;results=[]
   for m in machines:
    uc=m.uc;m.ensure(event);m.ensure(event+71);m.ensure(0x4009de50)
    uc.mem_write(event,bytes(72));uc.mem_write(event+8,struct.pack('>I',track));uc.mem_write(event+64,struct.pack('>I',identity))
    word=0x800000bd|(track<<13)
    uc.mem_write(BSS+32,bytes(128*4))
    if index<128:uc.mem_write(BSS+32+index*4,struct.pack('>I',word if valid else 0))
    uc.mem_write(BSS+0xb30+track*16,struct.pack('>IIII',identity,0,1,0))
    for i,r in enumerate(regs):uc.reg_write(r,0x24680100+i)
    uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A3,event);uc.reg_write(UC_M68K_REG_A7,0x47fdff00)
    try:uc.emu_start(layout['caller_commit']['address'],0x4009de50,count=10000)
    except Exception as exc:print('DEBUG',track,index,valid,hex(uc.reg_read(UC_M68K_REG_PC)),hex(uc.reg_read(UC_M68K_REG_A7)));raise
    assert uc.reg_read(UC_M68K_REG_PC)==0x4009de50
    results.append((observed(m),bytes(uc.mem_read(BSS,0xb70)),bytes(uc.mem_read(event,72))))
   assert results[0]==results[1],(track,index,valid)
   cases.append({'track':track,'slot':index,'valid_context':valid,'matches':True})
out={'firmware_modified':False,'cases':cases,'count':len(cases),'registers_materialized_SR_storage_and_event_match':True}
allocator_cases=[]
for event in [0,POOL,POOL+72,POOL+127*72,POOL+128*72,POOL+1]:
 results=[]
 for m in machines:
  uc=m.uc;m.ensure(0xdeadbee0)
  uc.mem_write(BSS+32,b''.join(struct.pack('>I',0x80000000+i) for i in range(128)))
  for i,r in enumerate(regs):uc.reg_write(r,0x24680100+i)
  uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A0,event);uc.reg_write(UC_M68K_REG_A7,0x47fdff00)
  uc.mem_write(0x47fdff00,struct.pack('>I',0xdeadbee0))
  uc.emu_start(0x47be063c,0xdeadbee0,count=10000)
  assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
  results.append((observed(m),bytes(uc.mem_read(BSS,0xb70))))
 assert results[0]==results[1],('allocator-return',event)
 allocator_cases.append({'event':hex(event),'matches':True})
out['allocator_return_cases']=allocator_cases;out['allocator_return_count']=len(allocator_cases)
pathlib.Path('outputs/Digitone-indexed-context-outer-ABI.json').write_text(json.dumps(out,indent=2));print('PASS',len(cases),'outer commit ABI cases')


