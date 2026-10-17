"""Exact cache bounds, invalidation and raw-copy ABI differential checks."""
import pathlib,sys,json,struct
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine,call
from unicorn.m68k_const import *
RAM,PTR,BSS,CACHE,POOL,STACK=0x47be0000,0x47be1000,0x47be1004,0x419a304c,0x4199da94,0x47fdff00
layout=json.loads(pathlib.Path('work/native-overlay-layout.json').read_text());build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
blob=pathlib.Path('work/cache-context-overlay.bin').read_bytes();stock=pathlib.Path('work/section-3.bin').read_bytes()
m=Machine(ddr=0x08000000);m.ensure(RAM);m.ensure(STACK);m.ensure(0x47bccf04);[m.ensure(0x40000000+i) for i in range(0,len(stock)+0x400,0x100000)];m.ensure(POOL);m.uc.mem_write(0x40000400,stock);m.uc.mem_write(RAM,blob);m.install_isa_patches_scoped(blob,RAM);m.install_isa_patches_scoped(stock[0x400ec23c-0x40000400:0x400ec284-0x40000400],0x400ec23c)
uc=m.uc;u32=lambda x:struct.pack('>I',x);rd=lambda a:struct.unpack('>I',uc.mem_read(a,4))[0]
def ready():
 uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
def invoke(a,args):
 v=call(m,a,args,stack_top=STACK,limit=100000);assert uc.reg_read(UC_M68K_REG_PC)==0xdeadbee0;return v
ready();bounds=0
for offset in range(-1,290):
 uc.reg_write(UC_M68K_REG_D0,CACHE+offset)
 actual=invoke(build['slot_address'],[])
 expected=0xa00+offset//72*4 if 0<=offset<288 and offset%72==0 else 0xffffffff
 assert actual==expected,(offset,hex(actual));bounds+=1
for i in range(4):
 invoke(layout['candidate_store']['address'],[CACHE+i*72,0x800000bd+i*0x2000])
 assert rd(BSS+2592+i*4)==0x800000bd+i*0x2000
 assert invoke(layout['snapshot']['address'],[CACHE+i*72])==rd(BSS+2592+i*4)
 invoke(layout['candidate_store']['address'],[CACHE+i*72,0]);assert rd(BSS+2592+i*4)==0
for bad in range(5):
 ready();header=[0x534c4332,2,0xb70,1]
 if bad<4:header[bad]^=1;uc.mem_write(BSS,struct.pack('>IIII',*header))
 else:uc.mem_write(PTR,u32(0))
 before=bytes(uc.mem_read(BSS,0xb70));invoke(layout['candidate_store']['address'],[CACHE,0x800000bd]);assert bytes(uc.mem_read(BSS,0xb70))==before
ready();regs=[UC_M68K_REG_D0+i for i in range(8)]+[UC_M68K_REG_A0+i for i in range(8)]
fallback=[];refresh_cases=[];pattern=0x47bc0000
for track in range(4):
 for root,raw in [(61,0),(59,5)]:
  ready();uc.mem_write(BSS+16,bytes(8));cache=CACHE+track*72
  uc.mem_write(pattern+track*0x3d0+0x3cb,bytes([root]));uc.mem_write(pattern+track*0x3d0+0x3ce,bytes([raw]))
  uc.reg_write(UC_M68K_REG_A7,STACK);uc.reg_write(UC_M68K_REG_A2,cache);uc.reg_write(UC_M68K_REG_A3,pattern);uc.reg_write(UC_M68K_REG_D4,track);uc.reg_write(UC_M68K_REG_SR,0x2700)
  uc.emu_start(layout['producer_capture']['address'],0x40093efc,count=100000)
  expected=0x80000000|root|((raw+1)<<7)|(track<<13)
  assert uc.reg_read(UC_M68K_REG_PC)==0x40093efc and rd(BSS+2592+track*4)==expected
  refresh_cases.append({'track':track,'root':root,'raw':raw,'word':hex(expected),'producer_refresh_passed':True})
for track in range(4):
 for reason in ['root','scale','busy','fault']:
  ready();uc.mem_write(BSS+16,bytes(8))
  uc.mem_write(pattern+track*0x3d0+0x3cb,bytes([128 if reason=='root' else 61]))
  uc.mem_write(pattern+track*0x3d0+0x3ce,bytes([35 if reason=='scale' else 0]))
  if reason in ['busy','fault']:uc.mem_write(BSS+(16 if reason=='busy' else 20),u32(1))
  cache=CACHE+track*72;invoke(layout['candidate_store']['address'],[cache,0x800000bd+track*0x2000])
  uc.reg_write(UC_M68K_REG_A7,STACK);uc.reg_write(UC_M68K_REG_A2,cache);uc.reg_write(UC_M68K_REG_A3,pattern);uc.reg_write(UC_M68K_REG_D4,track);uc.reg_write(UC_M68K_REG_SR,0x2700)
  uc.emu_start(layout['producer_capture']['address'],0x40093efc,count=100000)
  assert uc.reg_read(UC_M68K_REG_PC)==0x40093efc and rd(BSS+2592+track*4)==0
  fallback.append({'track':track,'reason':reason,'previous_candidate_cleared_by_producer':True})
ready();uc.mem_write(BSS+16,bytes(8))
abi=[]
for site in build['hooks']:
 for index in range(4):
  src=CACHE+index*72;dst=POOL+index*72;data=bytes((i*7+index)&255 for i in range(72));word=0x800000bd+index*0x2000
  uc.mem_write(src,data);invoke(layout['candidate_store']['address'],[src,word])
  start={r:0x11223000+j*0x100 for j,r in enumerate(regs)};start[UC_M68K_REG_A7]=STACK;start[UC_M68K_REG_A1]=0x400ec23c
  outputs=[]
  for patched in [False,True]:
   uc.mem_write(dst,bytes(72));invoke(layout['candidate_store']['address'],[dst,0])
   for r,v in start.items():uc.reg_write(r,v)
   uc.reg_write(UC_M68K_REG_SR,0x2700);uc.mem_write(STACK,u32(dst)+u32(src)+u32(72))
   uc.mem_write(site,stock[site-0x40000400:site-0x40000400+6])
   if patched:uc.mem_write(site,bytes.fromhex('4ef9' if site==0x4009344e else '4eb9')+u32(build['first_copy_address'] if site==0x4009344e else build['copy_address']))
   uc.ctl_remove_cache(site,site+6)
   end=site+6;uc.emu_start(site,end,count=100000);assert uc.reg_read(UC_M68K_REG_PC)==end,(hex(site),hex(uc.reg_read(UC_M68K_REG_PC)))
   outputs.append(({r:uc.reg_read(r) for r in regs},uc.reg_read(UC_M68K_REG_SR),bytes(uc.mem_read(dst,72))))
  assert outputs[0]==outputs[1],hex(site)
  assert rd(BSS+32+index*4)==word
  abi.append({'site':hex(site),'track':index,'registers_SR_bytes_match_stock':True,'context_copied':True})
result={'firmware_modified':False,'cache_bounds_cases':bounds,'cache_store_read_clear_cases':4,'invalid_header_store_cases':5,'producer_refresh_cases':refresh_cases,'producer_invalid_capture_cases':fallback,'raw_copy_ABI_cases':abi,'passed':True,'build':build}
pathlib.Path('outputs/Digitone-cache-context-helper-checks.json').write_text(json.dumps(result,indent=2));print('PASS',bounds,'cache bounds, four read/store/clear, five bad headers, eight copy ABI cases')




