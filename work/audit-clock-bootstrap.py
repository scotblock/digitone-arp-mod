import pathlib,sys,json,struct
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from emu import bootrom
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC
out={'writes':[]}
syx=pathlib.Path(r'inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
def install(m,flash,dspi):
 def write(uc,t,a,n,v,d):
  if 0xfc0c0000<=a<0xfc0c000c or 0xfc0b8000<=a<0xfc0b8100:
   out['writes'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(a),'size':n,'value':hex(v)})
 m.uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xfc000000,end=0xfcffffff)
r=bootrom.boot(syx,pathlib.Path('work/section-2.bin').read_bytes(),None,limit=2000000,chunk=100000,on_machine=install,ui_card=8,straps={0xec09401b:8},groups=7)
out.update(model_limitations=['Starts after hardware serial boot; PLL_CR/PLL_DR reset values are not seeded','LOCK/LOCKS and DDR-initialized flags are model inputs, not physical observations','Bounded to first two million instructions; not full boot or runtime writer certification'], control_registers={hex(k):hex(v) for k,v in r.m.ctlregs.items()}, stop=r.stop,instructions=r.instructions,flash_writes=len(r.flash_writes),mmio=[{'address':hex(a),'size':s,'value':hex(v)} for (a,s),v in r.mmio_writes.items()],pc=hex(r.m.uc.reg_read(UC_M68K_REG_PC)))
pathlib.Path('outputs/Digitone-clock-bootstrap-trace.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'stop':r.stop,'pc':out['pc'],'writes':out['writes']}))
