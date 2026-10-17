import pathlib,json,struct,hashlib,sys,time
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn.m68k_const import *
BASE,PTR,BSS,POOL=0x47be0000,0x47be1000,0x47be1004,0x4199da94
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text());build=json.loads(pathlib.Path('work/indexed-context-build.json').read_text())
machines=[]
for name in ['compact-hook','indexed-context']:
 m=Machine(ddr=0x08000000);m.ensure(BASE);m.ensure(0x47bccf04);m.ensure(0x47fdff00)
 blob=pathlib.Path('work/'+name+'-overlay.bin').read_bytes();m.uc.mem_write(BASE,blob);m.install_isa_patches_scoped(blob[:1892],BASE)
 m.uc.mem_write(PTR,struct.pack('>I',BSS-0x14100));m.uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
 m.uc.mem_write(BSS+32,b''.join(struct.pack('>I',0x80000000+i) for i in range(128)));machines.append(m)
def invoke(m,address,args):
 v=call(m,address,args,stack_top=0x47fdff00,limit=10000)
 assert m.uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 return v
started=time.monotonic();tested=0
for offset in range(9216):
 expected=offset//72*4 if offset%72==0 else 0xffffffff
 # Register ABI for the internal slot helper.
 machines[1].uc.reg_write(UC_M68K_REG_D0,POOL+offset)
 actual=invoke(machines[1],build['slot_offset_address'],[]);assert actual==expected,(offset,actual,expected)
 tested+=1
events=[POOL+i*72 for i in range(128)]+[POOL+i*72+d for i in range(128) for d in [-1,1,4,71]]+[0,0xffffffff,POOL-72,POOL+9216,POOL+9217,POOL+0x80000000]
for event in events:
 values=[invoke(m,layout['snapshot']['address'],[event]) for m in machines];assert values[0]==values[1],(hex(event),values)
 memories=[]
 for m in machines:
  invoke(m,layout['candidate_store']['address'],[event,0x87654321])
  memories.append(bytes(m.uc.mem_read(BSS,0xb70)))
 assert memories[0]==memories[1],hex(event)
 # Restore candidate values for the next snapshot comparison.
 for m in machines:m.uc.mem_write(BSS+32,b''.join(struct.pack('>I',0x80000000+i) for i in range(128)))
for bad in [0,1,2,3,4]:
 for m in machines:
  h=[0x534c4332,2,0xb70,1]
  if bad<4:h[bad]^=1
  m.uc.mem_write(PTR,struct.pack('>I',0 if bad==4 else BSS-0x14100));m.uc.mem_write(BSS,struct.pack('>IIII',*h))
 before=[bytes(m.uc.mem_read(BSS,0xb70)) for m in machines]
 for m in machines:invoke(m,layout['candidate_store']['address'],[POOL+127*72,0x12345678])
 assert before==[bytes(m.uc.mem_read(BSS,0xb70)) for m in machines]
out={'firmware_modified':False,'slot_offset_cases':tested,'snapshot_and_store_differential_events':len(events),'invalid_header_store_cases':5,'passed':True,'elapsed_seconds':time.monotonic()-started,'build':build}
pathlib.Path('outputs/Digitone-indexed-context-lookup-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
source=pathlib.Path('work/test-fast-pitch-hook-ABI.py').read_text().replace('work/fast-pitch-overlay.bin','work/indexed-context-overlay.bin').replace('outputs/Digitone-fast-pitch-hook-ABI.json','outputs/Digitone-indexed-context-ABI.json')
exec(compile(source,'indexed-context-ABI','exec'))
