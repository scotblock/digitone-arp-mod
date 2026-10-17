import pathlib,sys,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu import bootrom,longrun
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC
original=longrun.spin
def fastspin(*a,**kw):kw['fast']=True;return original(*a,**kw)
longrun.spin=fastspin
out={'writes':[],'seed_CR':'0xe400','firmware_modified':False}
def install(m,flash,dspi):
 m.ensure(0xfc044000);m.uc.mem_write(0xfc044000,struct.pack('>I',0xe400));m.uc.mem_write(0xfc044100,bytes(range(64)))
 def write(uc,t,a,n,v,d):
  if a<0xfc044004 or 0xfc044100<=a<0xfc044140:out['writes'].append(dict(pc=hex(uc.reg_read(UC_M68K_REG_PC)),address=hex(a),size=n,value=hex(v)))
 m.uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xfc044000,end=0xfc04413f)
def trace(m,done,pc):print('bootstrap',done,hex(pc),flush=True)
r=bootrom.boot(pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx'),pathlib.Path('work/section-2.bin').read_bytes(),pathlib.Path('work/section-3.bin').read_bytes(),limit=30000000,chunk=5000000,on_machine=install,ui_card=8,straps={0xec09401b:8},groups=7,trace=trace)
out.update(stop=r.stop,reached=hex(r.reached) if r.reached else None,instructions=r.instructions,main_os_matches=r.main_os_matches,pc=hex(r.m.uc.reg_read(UC_M68K_REG_PC)),CR=hex(struct.unpack('>I',r.m.uc.mem_read(0xfc044000,4))[0]),priority_bytes=bytes(r.m.uc.mem_read(0xfc044100,64)).hex(),flash_writes=len(r.flash_writes),limitations=['Documented DMA reset values explicitly seeded; serial ROM not executed','Native budget instruction totals are estimates','Bounded bootstrap execution; a limit stop does not establish full handoff preservation'])
pathlib.Path('outputs/Digitone-DMA-bootstrap-config-trace.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
