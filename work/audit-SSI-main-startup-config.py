"""Main application startup with documented DMA reset seed, PC only."""
import pathlib,json,struct
exec(pathlib.Path('work/watch-continuous-reserved-RAM.py').read_text().split('def canonical')[0])
from emu import dspboot,longrun
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7
box={};m,st,_=dspboot.run(str(SYX),pathlib.Path(paths.main_img).read_bytes(),limit=None,extra_hook=None,fast=True,coverage=False,verbose=False,machine_out=box,sdgate=True,esdhc=True,ddr=DDR)
m.ensure(0xfc044000);m.uc.mem_write(0xfc044000,struct.pack('>I',0xe400));m.uc.mem_write(0xfc044100,bytes(range(64)))
sp=m.uc.reg_read(UC_M68K_REG_A7);m.ensure(sp+4);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))
out={'SSI_registers':{},'writes':[],'seed_CR':'0xe400','seed_priority_bytes':bytes(range(64)).hex(),'firmware_modified':False}
def write(uc,t,a,n,v,d):
 if True:out['writes'].append(dict(pc=hex(uc.reg_read(UC_M68K_REG_PC)),address=hex(a),size=n,value=hex(v)))
m.uc.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xfc0c8000,end=0xfc0c807f)
cur=box['start_pc'];total=0
for j in range(6):
 cur,executed,why=longrun.spin(m,cur,30000000,fast=True);total+=executed
 print('main startup',total,hex(cur),why,flush=True)
 if why!='limit':break
out['SSI_registers']={hex(0xfc0c8000+i):hex(struct.unpack('>I',m.uc.mem_read(0xfc0c8000+i,4))[0]) for i in range(0,64,4)}
out.update(pc=hex(cur),stop=why,estimated_instructions=total,CR=hex(struct.unpack('>I',m.uc.mem_read(0xfc044000,4))[0]),priority_bytes=bytes(m.uc.mem_read(0xfc044100,64)).hex(),tasks=len(st['task_create_hits']),limitations=['Starts directly at MAIN OS entry, not physical serial boot','Boot flags 0x00140000 supplied','Existing synthetic card and bootstrap host helpers; no real DMA arbitration','Instruction totals are native block estimates; bounded run'])
pathlib.Path('outputs/Digitone-SSI-main-startup-config-trace.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
