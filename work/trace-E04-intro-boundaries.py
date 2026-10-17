from pathlib import Path
import sys,os,json,struct,time
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A7,UC_M68K_REG_SR,UC_M68K_REG_D0
payload=Path('work/os144/fallback-final-payload.bin').read_bytes()
out={'PC_only':True,'cases':[],'unblock':False,'limits':['Replays from newly matched direct-MAIN cold snapshots with modeled peripherals and inherited snapshots, not physical boot.','Flash/completion models, timer policy, ISA emulation, softfloat and bitmap acceleration still apply.']}
for name,syx in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx')]:
 root=Path('work/logo-compare-'+name+'-1').resolve()
 class Paths(bs.FirmwarePaths):
  @property
  def syx(self):return str(Path(syx).resolve())
 paths=Paths(str(root),Path(syx).name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
 row={'image':name,'events':[]};out['cases'].append(row);held={}
 def observe(m,ev,stage):
  held.update(m=m,ev=ev)
  if name=='E04':m.install_isa_patches_scoped(payload[:1784],0x47be0000);m.install_isa_patches_scoped(payload[2212:],0x47be08a4)
  def state(uc,pc,label):
   item={'label':label,'pc':hex(pc),'sp':hex(uc.reg_read(UC_M68K_REG_A7)),'sr':hex(uc.reg_read(UC_M68K_REG_SR)),'d0':hex(uc.reg_read(UC_M68K_REG_D0))}
   if name=='E04':item.update(pointer=bytes(uc.mem_read(0x47be1000,4)).hex(),header=list(struct.unpack('>4I',uc.mem_read(0x47be1004,16))))
   row['events'].append(item)
  def entering(uc,pc,size,data):
   sp=uc.reg_read(UC_M68K_REG_A7);ret,arg=struct.unpack('>II',uc.mem_read(sp,8));state(uc,pc,'stock_initializer_entry');row['events'][-1].update(argument=arg,return_pc=hex(ret))
   uc.hook_add(UC_HOOK_CODE,lambda uc,pc,size,data:state(uc,pc,'initializer_return'),begin=ret,end=ret)
  m.uc.hook_add(UC_HOOK_CODE,entering,begin=0x400ffed0,end=0x400ffed0)
  m.uc.hook_add(UC_HOOK_CODE,lambda uc,pc,size,data:state(uc,pc,'intro_exit'),begin=0x40091b0c,end=0x40091b0c)
 result=bs.boot_to_ui(paths.syx,paths.cold,budget=400_000_000,fast=True,options={'ddr':0x08000000,'unblock':False,'on_machine':observe})
 ev=held['ev'];row.update(up=result.up,intro_done=result.intro_done,mainloop=result.mainloop,stand_ins=ev.get('stand_ins'),satisfied=ev.get('satisfied'),satisfied_by={hex(k):v for k,v in ev.get('satisfied_by',{}).items()})
 print(name,'events',row['events'],'stand_ins',row['stand_ins'],flush=True)
 Path('outputs/Digitone-E04-intro-boundary-trace.json').write_text(json.dumps(out,indent=2)+'\n')
