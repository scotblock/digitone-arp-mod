from pathlib import Path
import sys,os,json,struct,time,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,dspboot,native,release,sparse
from emu.dtim import Dtims
from emu.longrun import _FastStepper
from emu.snapshot import save
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_SR

payload=Path('work/os144/fallback-final-payload.bin').read_bytes()
source=Path('work/os144-emulator-E02-engine/plusdrive.img')
out={'PC_only':True,'cases':[],'limits':['Timer expiry is modeled at native basic-block boundaries with assumed clock costs; no physical timing proof.','Direct MAIN entry with loader-matching boot flags and identical initialized emulator cards, not a physical loader/storage dump.','Cold flash-read shortcut and scoped ISA emulation remain. No host writes satisfy the delay semaphore.']}
dest=Path('outputs/Digitone-E04-native-startup-delay-checks.json')
for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:
 row={'image':name,'events':[],'delay_sem_writes':[],'failure':None};out['cases'].append(row);began=time.monotonic()
 try:
  root=Path('work/native-delay-'+name).resolve();root.mkdir(exist_ok=True)
  class Paths(bs.FirmwarePaths):
   @property
   def syx(self):return str(Path(syx).resolve())
  paths=Paths(str(root),Path(syx).name,str(Path('work/upstream/digiemu/devices').resolve()))
  Path(paths.snapdir).mkdir(parents=True,exist_ok=True);Path(paths.sections).mkdir(exist_ok=True)
  with source.open('rb') as src,open(paths.card,'wb') as dst:
   sparse.make_sparse(dst);sparse.extend(dst,source.stat().st_size)
   while chunk:=src.read(1024*1024):
    if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
  image=Path(imgfile).read_bytes();Path(paths.main_img).write_bytes(image)
  rel=release.identify_release(paths.syx,paths.devices_dir);release.write_device_overlay(rel,paths.overlay,paths.devices_dir);os.environ.update(paths.env())
  box={};m,st,_=dspboot.run(paths.syx,image,limit=None,coverage=False,patch_sem=False,patch_depack=True,ddr=0x08000000,machine_out=box)
  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))
  if name=='E04':m.ensure(0x47be0000);m.install_isa_patches_scoped(payload[:1784],0x47be0000);m.install_isa_patches_scoped(payload[2212:],0x47be08a4)
  done=0;timer=Dtims(m,channels=(1,),clear_stale=False)
  def mark(uc,pc,size,data):
   event={'pc':hex(pc),'estimated_instructions':done,'sr':hex(uc.reg_read(UC_M68K_REG_SR))}
   if pc==0x400fbd14:
    sp=uc.reg_read(UC_M68K_REG_A7);event.update(reference=int.from_bytes(uc.mem_read(0xfc074004,4),'big'),dtmr=bytes(uc.mem_read(0xfc074000,2)).hex(),vector_handler=bytes(uc.mem_read(0x40000184,4)).hex(),saved_d2=bytes(uc.mem_read(sp+8,4)).hex(),return_to_delay_caller=bytes(uc.mem_read(sp+16,4)).hex())
   row['events'].append(event)
  for pc in [0x4029c4b0,0x4000055a,0x400fbd14,0x400fbc58,0x400fbc86,0x400ffed0,0x47be08a4]:m.uc.hook_add(UC_HOOK_CODE,mark,begin=pc,end=pc)
  def semwrite(uc,access,address,size,value,data):
   row['delay_sem_writes'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'estimated_instructions':done,'address':hex(address),'size':size,'value':value})
  m.uc.hook_add(UC_HOOK_MEM_WRITE,semwrite,begin=0x419eaeec,end=0x419eaef3)
  pc=box['start_pc'];budget=native.NativeBudget(m.uc);parked=False;window_spins=0;window_tasks=0;next_window=10_000_000
  while done<600_000_000:
   step=min(100_000,timer.step(done,100_000));blocks=max(1,int(step/_FastStepper.PER_BLOCK));budget.state.left=blocks
   m.uc.emu_start(pc,0);done+=max(1,int(blocks*_FastStepper.PER_BLOCK));timer.service(done);pc=m.uc.reg_read(UC_M68K_REG_PC)
   if m.halt_vec is not None:break
   if done>=next_window:
    spins=st['spin'];tasks=len(st['task_create_hits'])
    if spins-window_spins>int(10_000_000/_FastStepper.PER_BLOCK)//4 and tasks==window_tasks:parked=True;break
    window_spins=spins;window_tasks=tasks;next_window+=10_000_000
  row.update(cold_pc=hex(pc),estimated_instructions=done,parked=parked,halt_vec=m.halt_vec,timer_fired=dict(timer.fired),completion_kicks=st['sem_kicks'],depack_clamps=st['depack_clamps'],task_count=len(st['task_create_hits']))
  assert st['sem_kicks']==0 and timer.fired[1]>=3 and m.halt_vec is None and parked
  assert sum(e['pc']=='0x400fbc58' for e in row['events'])>=3
  if name=='E04':assert bytes(m.uc.mem_read(0x47be0000,len(payload)))==payload
  save(m,paths.cold,extra={'tasks':{hex(k):v for k,v in st['task_create_hits'].items()},'n':done})
  if m.esdhc.card.path:m.esdhc.card.flush()
  bs._close_card(m);del m,budget
  held={}
  def intro_observe(mm,ev,stage):
   held['ev']=ev
   if name=='E04':mm.install_isa_patches_scoped(payload[:1784],0x47be0000);mm.install_isa_patches_scoped(payload[2212:],0x47be08a4)
  result=bs.boot_to_ui(paths.syx,paths.cold,budget=400_000_000,fast=True,options={'ddr':0x08000000,'unblock':False,'on_machine':intro_observe})
  row['intro']={'up':result.up,'intro_done':result.intro_done,'mainloop':result.mainloop,'stand_ins':held['ev'].get('stand_ins'),'general_satisfactions':held['ev'].get('satisfied')}
  assert result.up and not held['ev'].get('stand_ins',{}).get('completion_sem',0)
  row['passed']=True
 except Exception:row['failure']=traceback.format_exc();row['passed']=False;print(row['failure'],flush=True)
 row['seconds']=time.monotonic()-began;dest.write_text(json.dumps(out,indent=2)+'\n');print('native delay',name,row.get('passed'),row.get('timer_fired'),flush=True)
