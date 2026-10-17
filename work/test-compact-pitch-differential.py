import pathlib
exec(pathlib.Path('work/test-compact-hook-helpers.py').read_text().split('for track in [0,1,2,3,4,127')[0])
cases=[]
for track in range(4):
 for bad in ['valid','kind','state','track','flags','identity','cached-kind','cached-state','cached-track','cached-flags','cached-identity','selected','disabled','cookie','busy','context','header','pointer']:
  results=[]
  for m in machines:
   uc=m.uc;event=0x4199da94+track*72;identity=0x419c38c0+track*0x504
   for address in [event,0x41345f08+track*72,0x41344530+track*40+24,0x41345620+track*4]:m.ensure(address)
   data=bytearray(72)
   for off,value in [(0,0),(4,1),(8,track),(40,1<<19),(64,identity)]:data[off:off+4]=struct.pack('>I',value)
   cache=bytearray(data)
   changes={'kind':(0,1),'state':(4,0),'track':(8,4),'flags':(40,0),'identity':(64,identity+4)}
   key=bad.removeprefix('cached-')
   if key in changes:
    off,v=changes[key];target=cache if bad.startswith('cached-') else data;target[off:off+4]=struct.pack('>I',v)
   uc.mem_write(event,bytes(data));uc.mem_write(0x41345f08+track*72,bytes(cache))
   uc.mem_write(0x41344530+track*40+24,struct.pack('>I',identity+(4 if bad=='selected' else 0)))
   uc.mem_write(0x41345620+track*4,struct.pack('>I',0 if bad=='disabled' else 1))
   uc.mem_write(PTR,struct.pack('>I',0 if bad=='pointer' else BSS-0x14100))
   uc.mem_write(BSS,struct.pack('>IIII',0 if bad=='header' else 0x534c4332,2,0xb70,1))
   word=0x800000bd|(track<<13)
   record=BSS+0xb30+track*16
   uc.mem_write(record,struct.pack('>IIII',identity,0 if bad=='context' else word,1 if bad=='busy' else 0,0 if bad=='cookie' else 0x80000000|track))
   for i,reg in enumerate(regs[:-1]):uc.reg_write(reg,0x24680100+i)
   call(m,layout['pitch']['address'],[event,61+track],stack_top=0x47fdff00,limit=10000)
   assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0
   results.append((observed_registers(m),bytes(uc.mem_read(event,72)),bytes(uc.mem_read(record,16))))
  assert results[0]==results[1],(track,bad,results)
  cases.append({'track':track,'predicate':bad,'matches':True})
out={'firmware_modified':False,'cases':cases,'count':len(cases),'registers_materialized_SR_event_and_record_match':True}
pathlib.Path('outputs/Digitone-compact-hook-pitch-differential.json').write_text(json.dumps(out,indent=2))
print('PASS',len(cases),'pitch differential cases')
