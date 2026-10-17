"""Native copy boundaries and documented cache-state counterexamples, PC only."""
import pathlib,sys,json,struct,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu.harness import Machine
from unicorn.m68k_const import *
RAM=0x47be0000;PTR=RAM+0x1000;BSS=PTR+4
blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes();stock=pathlib.Path('work/section-3.bin').read_bytes();STAGE=0x40000400+len(stock);TABLE=RAM+1904
def u32(x):return struct.pack('>I',x)
cases=[]
for words in [581,473,579]:
 m=Machine(ddr=0x08000000);uc=m.uc
 for address in [RAM,STAGE,0x47fffffc]+list(range(0x40000000,0x40300000,0x100000)):m.ensure(address)
 uc.mem_write(0x40000400,stock);uc.mem_write(RAM,bytes([0xa5])*0x20000)
 code=bytes.fromhex('41f9')+u32(STAGE+0x100)+bytes.fromhex('43f9')+u32(RAM)+bytes.fromhex('203c')+u32(words)+bytes.fromhex('22d853806600fffa4ef940001df4')
 uc.mem_write(STAGE,code);uc.mem_write(STAGE+0x100,blob)
 uc.mem_write(0x47fffffc,u32(0x4000053e));uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,0x47fffffc)
 m.install_isa_patches_scoped(stock[0x40001df4-0x40000400:0x40001dfe-0x40000400],0x40001df4)
 uc.emu_start(STAGE,0x4000053e,count=10000)
 copied=bytes(uc.mem_read(RAM,len(blob)));table=bytes(uc.mem_read(TABLE,420))
 assert uc.reg_read(UC_M68K_REG_PC)==0x4000053e
 assert (table==blob[1904:2324])==(words==581)
 assert bytes(uc.mem_read(RAM+words*4,16))==bytes([0xa5])*16
 cases.append({'copy_longs':words,'whole_image_matches':copied==blob,'table_matches':table==blob[1904:2324],'table_bytes_missing':sum(x!=y for x,y in zip(table,blob[1904:2324])),'next_16_bytes_untouched':True})
# Execute the actual relocated loader tail; its input pointer/flags are fixtures.
loader=pathlib.Path('work/section-2.bin').read_bytes();base=0x800003fc
tail=loader[0x80007300-base:0x80007456-base]
m=Machine(ddr=0x08000000);uc=m.uc
for a in [0x80000000]+list(range(0x40000000,0x40300000,0x100000)):m.ensure(a)
uc.mem_write(0x8000f000,tail);uc.mem_write(0x8000f00c,u32(0x40000400));uc.mem_write(0x40000400,stock)
uc.reg_write(UC_M68K_REG_SR,0x2700);uc.reg_write(UC_M68K_REG_A7,0x8000ff00);uc.reg_write(UC_M68K_REG_D2,0x00140000)
m.install_isa_patches_scoped(tail,0x8000f000);uc.emu_start(0x8000f136,0x400004e8,count=1000)
assert uc.reg_read(UC_M68K_REG_PC)==0x400004e8 and m.ctlregs[2]==0x000cc100
loader_tail={'reached':'0x400004e8','programmed_CACR':hex(m.ctlregs[2]),'data_cache_enabled':bool(m.ctlregs[2]&0x80000000),'instruction_cache_enabled':bool(m.ctlregs[2]&0x8000),'preconditions':'Entered after reader return at relocated tail; descriptor destination and boot flags explicitly supplied. Full loader/decompression not executed.'}
# A small value-coherence model, not a hardware simulation: every table byte has
# an old valid cache value, then copy writes occur, then stock invalidate-all.
def model(mode,invalidate,push=False):
 memory=bytearray([0xa5]*420);old_cache=bytearray([0x5a]*420);dirty=False
 for i,value in enumerate(blob[1904:2324]):
  if mode=='copyback':old_cache[i]=value;dirty=True
  else:memory[i]=value
 if push and dirty:memory[:]=old_cache;dirty=False
 if invalidate:old_cache=None;dirty=False
 observed=old_cache if old_cache is not None else memory
 return bytes(observed)==blob[1904:2324]
cache_cases=[]
for mode,inv,push,expected in [('disabled',True,False,True),('disabled',False,False,False),('copyback',True,False,False),('copyback',True,True,True)]:
 got=model(mode,inv,push);assert got==expected
 cache_cases.append({'copy_mode':mode,'stock_invalidation':inv,'hypothetical_push_before_invalidate':push,'table_visible_after_handoff':got})
result={'firmware_modified':False,'native_copy_cases':cases,'actual_loader_tail':loader_tail,'cache_state_cases':cache_cases,'manual':'https://www.nxp.com/docs/en/reference-manual/MCF54418RM.pdf','manual_sections':['6.2.2','6.3.1','6.3.2','6.4.6'],'limits':['The small cache model follows the cited state rules; it is not a measured cache or timing implementation.','The loader-tail test supplies the descriptor pointer and boot flags; it does not prove full loader reachability or pre-tail DDR visibility.','No extra cache flush or startup guard was installed.']}
pathlib.Path('outputs/Digitone-table-copy-cache-preconditions.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
