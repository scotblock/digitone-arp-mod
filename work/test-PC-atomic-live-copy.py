"""Isolated PC alternative: serialize stock bytes plus metadata against
maskable CPU preemption. Not installed into startup or a firmware container."""
from pathlib import Path
exec(Path('work/test-PC-live-reset-overlap.py').read_text().split('results=[]')[0])
base=0x47be3600;blob=Path('work/os144/PC_ONLY-live-capture-code.bin').read_bytes();item=LIVE['layout']['live_copy'];original=blob[item['address']-LIVE['base']:item['address']-LIVE['base']+item['size']]
body=original[40:-16];assert original[:22].hex()=='2f2f000c2f2f000c2f2f000c4eb9400fbad84fef000c'
body=body.replace(bytes.fromhex('202f004c'),bytes.fromhex('202f0054')).replace(bytes.fromhex('202f0048'),bytes.fromhex('202f0050')).replace(bytes.fromhex('2f2f0048'),bytes.fromhex('2f2f0050'))
prefix=bytes.fromhex('4feffff82e8740c746fc27002f2f00142f2f00142f2f00144eb9400fbad84fef000c')
save=bytes.fromhex('4fefffc048d77fff40c03f40003c46fc2700');restore=bytes.fromhex('302f003c46c04cd77fff4fef0040')
merge=bytes.fromhex('202f001c7200322f003c02800000ffe002810000001f80813f40003c202f00402f40001c')
code=prefix+save+body+merge+restore+bytes.fromhex('4fef00084e75')
Path('work/os144/PC_ONLY-atomic-live-copy.bin').write_bytes(code)
p=0
while p<len(code):
 i=cfisa.decode(lambda off:int.from_bytes(code[p+off:p+off+2],'big'),base+p);assert not i.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) and not move_restriction(int.from_bytes(code[p:p+2],'big')),(hex(base+p),i.op);p+=i.length
assert p==len(code)
def install(m):m.load(code,base);m.install_isa_patches_scoped(code,base)
def invoke(m,entry,dest,src,length,sr):
 u=m.uc;stack=0x47fdff00;u.mem_write(stack,u32(0xdeadbee0)+u32(dest)+u32(src)+u32(length));u.reg_write(UC_M68K_REG_SR,sr);u.reg_write(UC_M68K_REG_A7,stack);u.emu_start(entry,0xdeadbee0,count=100000);assert u.reg_read(UC_M68K_REG_PC)==0xdeadbee0
 return {'regs':[u.reg_read(r) for r in REGS if r!=UC_M68K_REG_PC],'bytes':bytes(u.mem_read(dest,72)).hex()}
controls=[]
for mode in ['known','unknown_source','short','unready','unknown_destination']:
 for sr in [0x201f,0x231f,0x271f]:
  states=[]
  for entry in [0x400fbad8,base]:
   m=prepared();install(m);u=m.uc;event=call(m,0x400ffff2,[],stack_top=RESETSTACK,limit=10000);dest=event if mode!='unknown_destination' else 0x419ef000;src=0x43220348+64*72 if mode!='unknown_source' else 0x43227000;length=68 if mode=='short' else 72;m.ensure(src);u.mem_write(src,bytes(range(72)));u.mem_write(LIVE['state']+64*4,u32(0x800000be));u.mem_write(0x47be1024,u32(0x12345678));u.mem_write(0x47be1010,u32(0 if mode=='unready' else 1))
   for j,r in enumerate(REGS[:-2]):
    if r!=UC_M68K_REG_A7:u.reg_write(r,0x12340000+j)
   states.append(invoke(m,entry,dest,src,length,sr));actual=rd(u,0x47be1024)
  assert states[0]==states[1],(mode,hex(sr),states)
  expected={'known':0x800000be,'unknown_source':0,'short':0x12345678,'unready':0x12345678,'unknown_destination':0x12345678}[mode];assert actual==expected,(mode,hex(actual))
  controls.append({'mode':mode,'incoming_SR':hex(sr),'stock_bytes_registers_stack_SR_match':True,'metadata':hex(actual)})
# Attempt a maskable producer rewrite exactly where the former race occurred.
m=prepared();install(m);u=m.uc;event=call(m,0x400ffff2,[],stack_top=RESETSTACK,limit=10000);src=0x43220348+64*72;m.ensure(src);desc=bytearray(72);desc[4:8]=u32(1);desc[0x18]=64;desc[0x10:0x12]=(100<<8).to_bytes(2,'big');u.mem_write(src,bytes(desc));u.mem_write(LIVE['state']+64*4,u32(0x800000be))
attempts=[];deferred=[]
def would_preempt(u,pc,n,d):
 mask=(u.reg_read(UC_M68K_REG_SR)>>8)&7;attempts.append({'pc':hex(pc),'mask':mask,'interrupt_level':6,'admitted':6>mask})
 if 6>mask:u.mem_write(LIVE['state']+64*4,u32(0x800000bc))
 else:deferred.append(True)
ret=base+len(prefix)-4;h=u.hook_add(UC_HOOK_CODE,would_preempt,begin=ret,end=ret);invoke(m,base,event,src,72,0x201f);u.hook_del(h)
assert attempts and deferred and not any(x['admitted'] for x in attempts) and bytes(u.mem_read(event,72))==bytes(desc) and rd(u,0x47be1024)==0x800000be
# Model delivery after returning, when the original interrupt mask is restored.
assert (u.reg_read(UC_M68K_REG_SR)>>8)&7==0;u.mem_write(LIVE['state']+64*4,u32(0x800000bc));assert rd(u,0x47be1024)==0x800000be
out={'PC_only':True,'not_installed_in_startup':True,'code_address':hex(base),'code_bytes':len(code),'strict_static_checks':True,'controls':controls,'deferred_preemption':attempts,'passed':True,'limits':['Admission is checked against documented SR mask semantics, not a real interrupt-dispatch execution.','No hardware duration/cache proof or exclusion of DMA/nonmaskable writers.','Does not protect allocation-to-publication across a full pool reset.']}
Path('outputs/Digitone-E04-PC-atomic-live-copy.json').write_text(json.dumps(out,indent=2));print('PASS',len(controls),'stock-equivalence cases and deferred maskable rewrite;',len(code),'bytes')
