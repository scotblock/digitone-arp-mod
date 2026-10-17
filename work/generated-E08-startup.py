from pathlib import Path
import sys,os,json,struct,time,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,dspboot,native,release,sparse
from emu.dtim import Dtims
from emu.longrun import _FastStepper
from emu.snapshot import save
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_SR

payload=Path('work/os144/E08-PC-layout-payload.bin').read_bytes()
source=Path('work/os144-emulator-E02-engine/plusdrive.img')
out={'PC_only':True,'cases':[],'limits':['Timer expiry is modeled at native basic-block boundaries with assumed clock costs; no physical timing proof.','Direct MAIN entry with loader-matching boot flags and identical initialized emulator cards, not a physical loader/storage dump.','Cold flash-read shortcut and scoped ISA emulation remain. No host writes satisfy the delay semaphore.']}
dest=Path('outputs/Digitone-E08-PC-startup-comparison.json')
for name,syx,imgfile,cardfile in [('E08_restored', 'work/os144/E08-PC-path-candidate.syx', 'work/os144/E08-PC-layout-main.bin', 'work/os144/PC_ONLY-saved-mirror-valid_first.img')]:
 row={'image':name,'events':[],'delay_sem_writes':[],'failure':None};out['cases'].append(row);began=time.monotonic()
 try:
  source=Path(cardfile)
  root=Path('work/E08-startup-'+name).resolve();root.mkdir(exist_ok=True)
  class Paths(bs.FirmwarePaths):
   @property
   def syx(self):return str(Path(syx).resolve())
  paths=Paths(str(root),Path(syx).name,str(Path('work/upstream/digiemu/devices').resolve()))
  Path(paths.snapdir).mkdir(parents=True,exist_ok=True);Path(paths.sections).mkdir(exist_ok=True)
  with source.open('rb') as src,open(paths.card,'wb') as dst:
   sparse.make_sparse(dst);sparse.extend(dst,source.stat().st_size)
   while chunk:=src.read(1024*1024):
    if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
  from dt2.container import sections
  cc,ee=sections(Path(syx));_,off,n,_=next(e for e in ee if e[0]==7);blob=cc[off:off+n]
  assert blob==Path('work/os144/section-7-stored.bin').read_bytes()
  Path(paths.sections,'section_7_BLOB.bin').write_bytes(blob)
  row['DSP_section_from_candidate_verified']=True
  image=Path(imgfile).read_bytes();Path(paths.main_img).write_bytes(image)
  rel=release.identify_release(paths.syx,paths.devices_dir);release.write_device_overlay(rel,paths.overlay,paths.devices_dir);os.environ.update(paths.env())
  box={};m,st,_=dspboot.run(paths.syx,image,limit=None,coverage=False,patch_sem=False,patch_depack=True,ddr=0x08000000,machine_out=box)
  sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))
  if name.startswith('E08'):m.ensure(0x47be0000)
  row['strict_failures']=[];row['strict_executed']={};row['phase_events']=[];row['copied_components_verified']=False
  def install_strict(mm,stage):
   if not name.startswith('E08'):return
   def strict(u,pc,n,d):
    ins=cfisa.decode(lambda off:int.from_bytes(u.mem_read(pc+off,2),'big'),pc)
    bad=move_restriction(int.from_bytes(u.mem_read(pc,2),'big'))
    if bad or ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) or (ins.flags&cfisa.PRIV and not u.reg_read(UC_M68K_REG_SR)&0x2000):
     row['strict_failures'].append({'pc':hex(pc),'op':ins.op,'stage':stage,'reason':bad});raise AssertionError(row['strict_failures'][-1])
    row['strict_executed'][stage]=row['strict_executed'].get(stage,0)+1
   for r in cfg['regions']:
    data=image[r['base']-0x40000400:r['base']-0x40000400+r['bytes']] if r['base']<0x47be0000 else payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']]
    mm.install_isa_patches_scoped(data,r['base']);mm.uc.hook_add(UC_HOOK_CODE,strict,begin=r['base'],end=r['base']+r['bytes']-1)
  install_strict(m,'cold')
  def copied(u,pc,n,d):
   for r in cfg['components']:
    off=r['base']-0x47be0000;assert bytes(u.mem_read(r['base'],r['bytes']))==payload[off:off+r['bytes']],r['name']
   assert bytes(u.mem_read(0x47be2860,400))==bytes(400) and int.from_bytes(u.mem_read(0x47be2840,4),'big')==0
   row['copied_components_verified']=True
  def phase(u,pc,n,d):row['phase_events'].append({'pc':hex(pc),'phase':hex(int.from_bytes(u.mem_read(0x47be2840,4),'big'))})
  if name.startswith('E08'):
   # Dirty only the destination before the native copier. No executable helper is host-loaded.
   m.uc.mem_write(0x47be3800,bytes([0xa5])*0x1004);m.uc.mem_write(0x47be2860,bytes([0xa5])*400)
   m.uc.hook_add(UC_HOOK_CODE,copied,begin=0x4029c518,end=0x4029c518)
   for pc0 in [0x4000053e,0x4009d0d8,0x4008d3fa]:m.uc.hook_add(UC_HOOK_CODE,phase,begin=pc0,end=pc0)
   if name=='E08_disabled':
    def corrupt(u,pc,n,d):u.mem_write(0x47be1000,struct.pack('>I',0xffffffff))
    m.uc.hook_add(UC_HOOK_CODE,corrupt,begin=0x47be3400,end=0x47be3400)
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
  if name.startswith('E08'):assert row['copied_components_verified'] and not row['strict_failures']
  if name.startswith('E08'):row['phase_after_cold']=hex(int.from_bytes(m.uc.mem_read(0x47be2840,4),'big'));assert row['phase_after_cold']=='0x4c495645';row['READY']=int.from_bytes(m.uc.mem_read(0x47be1010,4),'big');assert row['READY']==(0 if name=='E08_disabled' else 1)
  save(m,paths.cold,extra={'tasks':{hex(k):v for k,v in st['task_create_hits'].items()},'n':done})
  if m.esdhc.card.path:m.esdhc.card.flush()
  bs._close_card(m);del m,budget
  held={}
  def intro_observe(mm,ev,stage):
   held['ev']=ev
   row['DSP_model']=type(ev['dsplink']).__name__;assert row['DSP_model']=='DspCpu'
   if name.startswith('E08'):install_strict(mm,'intro')
  result=bs.boot_to_ui(paths.syx,paths.cold,out=paths.gui_raw,budget=400_000_000,fast=True,options={'ddr':0x08000000,'unblock':False,'on_machine':intro_observe})
  row['intro']={'up':result.up,'intro_done':result.intro_done,'mainloop':result.mainloop,'stand_ins':held['ev'].get('stand_ins'),'general_satisfactions':held['ev'].get('satisfied')}
  assert result.up and not held['ev'].get('stand_ins',{}).get('completion_sem',0)
  row['ui_snapshot']=paths.gui_raw
  row['packaged_helpers_host_loaded']=False
  assert not row['strict_failures']
  row['passed']=True
 except Exception:row['failure']=traceback.format_exc();row['passed']=False;print(row['failure'],flush=True)
 row['seconds']=time.monotonic()-began;dest.write_text(json.dumps(out,indent=2)+'\n');print('native delay',name,row.get('passed'),row.get('timer_fired'),flush=True)

out['passed']=all(r.get('passed') for r in out['cases']);dest.write_text(json.dumps(out,indent=2));
if not out['passed']:raise SystemExit(1)
