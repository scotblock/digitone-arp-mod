"""Stock bootstrap from its reset entry: bounded cache/control trace, PC only."""
import pathlib,sys,json,hashlib,time
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom,longrun
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import *
syx=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
boot=pathlib.Path('work/section-2.bin').read_bytes();main=pathlib.Path('work/section-3.bin').read_bytes()
out={'firmware_modified':False,'cache_writes':[],'milestones':[],'chunks':[],'before':hashlib.sha256(syx.read_bytes()).hexdigest()};start=time.monotonic()
original=longrun.spin
def fastspin(*a,**kw):kw['fast']=True;return original(*a,**kw)
longrun.spin=fastspin
def install(m,flash,dspi):
 def record(uc,pc,n,d):
  raw=bytes(uc.mem_read(pc,4))
  if raw[:2]!=bytes.fromhex('4e7b') or int.from_bytes(raw[2:],'big')&4095 not in [2,4,5,6,7,12,13,14,15]:return
  word=int.from_bytes(uc.mem_read(pc+2,2),'big');reg=(UC_M68K_REG_A0 if word&0x8000 else UC_M68K_REG_D0)+((word>>12)&7)
  out['cache_writes'].append({'pc':hex(pc),'selector':hex(word&4095),'value':hex(uc.reg_read(reg))})
 for image,base in [(boot[4:],0x80000400),(bootrom.container_section(syx,4)[8:],0x80000408)]:
  for i in range(0,len(image)-3,2):
   if image[i:i+2]==bytes.fromhex('4e7b') and int.from_bytes(image[i+2:i+4],'big')&4095 in [2,4,5,6,7,12,13,14,15]:m.uc.hook_add(UC_HOOK_CODE,record,begin=base+i,end=base+i)
 for pc in [0x80007400,0x8000f100,0x8000f136,0x8000f14c]:
  m.uc.hook_add(UC_HOOK_CODE,lambda uc,a,n,d:out['milestones'].append({'pc':hex(a),'controls':{hex(k):hex(v) for k,v in m.ctlregs.items()}}),begin=pc,end=pc)
def trace(m,done,pc):
 out['chunks'].append({'estimated_instructions':done,'pc':hex(pc),'CACR':hex(m.ctlregs.get(2,0))});print('loader',done,hex(pc),'CACR',hex(m.ctlregs.get(2,0)),flush=True)
r=bootrom.boot(syx,boot,main,limit=300000000,chunk=10000000,on_machine=install,ui_card=8,straps={0xec09401b:8},groups=7,trace=trace)
out.update(stop=r.stop,reached=hex(r.reached) if r.reached else None,main_os_matches=r.main_os_matches,instructions=r.instructions,pc=hex(r.m.uc.reg_read(UC_M68K_REG_PC)),controls={hex(k):hex(v) for k,v in r.m.ctlregs.items()},flash_reads=r.flash_reads,flash_writes=r.flash_writes,panel_queries=r.panel_queries,seconds=time.monotonic()-start,after=hashlib.sha256(syx.read_bytes()).hexdigest())
assert out['before']==out['after'] and not r.flash_writes
pathlib.Path('outputs/Digitone-stock-loader-cache-continuity.json').write_text(json.dumps(out,indent=2))
if r.reached is not None:bootrom.save_handoff(r,'work/stock-loader-cache-handoff.bin')
print('RESULT',out['stop'],out['pc'],'seconds',out['seconds'],flush=True)
