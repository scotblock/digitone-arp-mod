from pathlib import Path
import sys, os, json, time, struct, hashlib, shutil
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs, dspboot, native, release, sparse, symbols
from emu.snapshot import save
from emu.longrun import _FastStepper
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_A7, UC_M68K_REG_SR

out={'PC_only':True,'cases':[],'limits':['Matched direct MAIN resets, not physical loader/persistent state.','Both images start with byte-identical initialized emulator drive copies.','Flash reads, peripheral models, scoped ISA emulation and bitmap/softfloat accelerations remain present.','Cold instruction totals use a native basic-block estimate. No physical cache or timing simulation.']}
report=Path('outputs/Digitone-E04-logo-startup-comparison.json')
payload=Path('work/os144/fallback-final-payload.bin').read_bytes()
source=Path('work/os144-emulator-E02-engine/plusdrive.img')
for name,syx,imgfile in [('stock','outputs/stock-recovery/Digitone_and_Digitone_Keys_OS1.44_STOCK.syx','work/os144/section-3.bin'),('E04','outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx','work/os144/emulator-E04-main.bin')]:
 for sem in [True,False]:
  row={'image':name,'completion_signal_shortcut':sem,'cold_events':[],'intro':[]};out['cases'].append(row)
  started=time.monotonic()
  try:
   root=Path(f'work/logo-compare-{name}-{int(sem)}').resolve();root.mkdir(exist_ok=True)
   class Paths(bs.FirmwarePaths):
    @property
    def syx(self):return str(Path(syx).resolve())
   paths=Paths(str(root),Path(syx).name,str(Path('work/upstream/digiemu/devices').resolve()))
   Path(paths.snapdir).mkdir(parents=True,exist_ok=True)
   # Fresh copy every run, preserving sparse zeros. No original card is modified.
   with source.open('rb') as src,open(paths.card,'wb') as dst:
    sparse.make_sparse(dst);sparse.extend(dst,source.stat().st_size)
    while chunk:=src.read(1024*1024):
     if chunk.strip(b'\0'):dst.seek(src.tell()-len(chunk));dst.write(chunk)
   image=Path(imgfile).read_bytes();Path(paths.sections).mkdir(exist_ok=True);Path(paths.main_img).write_bytes(image)
   rel=release.identify_release(str(Path(syx).resolve()),str(Path('work/upstream/digiemu/devices').resolve()))
   release.write_device_overlay(rel,paths.overlay,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
   prof=symbols.resolve(image,load_addr=0x40000400)
   row['symbols']={k:hex(getattr(prof,k)) if getattr(prof,k,None) is not None else None for k in ['entry','pend_call','completion_sem','depack_copy','intro_done','intro_pit3_isr','frame_sem','mainloop']}
   box={};m,st,_=dspboot.run(paths.syx,image,limit=None,coverage=False,patch_sem=sem,patch_depack=True,ddr=0x08000000,machine_out=box)
   sp=m.uc.reg_read(UC_M68K_REG_A7);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000))
   row['entry_flags_fixture']='0x00140000 at SP+4, matching earlier loader-derived boot flags; loader not executed in this test'
   def watch(uc,pc,size,data):
    if len(row['cold_events'])<40:row['cold_events'].append({'pc':hex(pc),'sp':hex(uc.reg_read(UC_M68K_REG_A7)),'sr':hex(uc.reg_read(UC_M68K_REG_SR))})
   for address in [0x400ffed0,0x47be08a4,0x47be0642,prof.pend_call]:m.uc.hook_add(UC_HOOK_CODE,watch,begin=address,end=address)
   if name=='E04':
    m.ensure(0x47be0000);m.install_isa_patches_scoped(payload[:1784],0x47be0000);m.install_isa_patches_scoped(payload[2212:],0x47be08a4)
   pc=box['start_pc'];budget=native.NativeBudget(m.uc);done=0;parked=False
   blocks=int(10_000_000/_FastStepper.PER_BLOCK)
   while done<600_000_000:
    before=st['spin'];tasks=len(st['task_create_hits']);budget.state.left=blocks
    m.uc.emu_start(pc,0);pc=m.uc.reg_read(UC_M68K_REG_PC);done+=10_000_000
    if m.halt_vec is not None:break
    if st['spin']-before>blocks//4 and tasks==len(st['task_create_hits']):parked=True;break
   row['cold']={'pc':hex(pc),'estimated_instructions':done,'parked':parked,'halt_vec':m.halt_vec,'completion_kicks':st['sem_kicks'],'depack_clamps':st['depack_clamps'],'tasks':st['task_create_hits'],'pointer':bytes(m.uc.mem_read(0x47be1000,4)).hex() if name=='E04' else None,'payload_exact':bytes(m.uc.mem_read(0x47be0000,len(payload)))==payload if name=='E04' else None}
   if sem and parked:
    save(m,paths.cold,extra={'n':done,'tasks':{hex(k):v for k,v in st['task_create_hits'].items()}})
    if m.esdhc.card.path:m.esdhc.card.flush()
   bs._close_card(m);del m,budget
   if sem and parked:
    for unblock in [True,False]:
     marks=[]
     def observe(mm,ev,stage):
      if name=='E04':
       mm.install_isa_patches_scoped(payload[:1784],0x47be0000);mm.install_isa_patches_scoped(payload[2212:],0x47be08a4)
     def progress(ev):
      if ev.text:marks.append(ev.text)
     result=bs.boot_to_ui(paths.syx,paths.cold,budget=400_000_000,fast=True,progress=progress,options={'ddr':0x08000000,'unblock':unblock,'on_machine':observe})
     row['intro'].append({'unblock':unblock,'up':result.up,'total':result.total,'lit':result.lit,'mainloop':result.mainloop,'intro_done':result.intro_done,'flipped_at':result.flipped_at,'progress':marks})
     print(name,'intro unblock',unblock,'up',result.up,'intro_done',result.intro_done,flush=True)
   print(name,'completion shortcut',sem,'cold PC',row['cold']['pc'],'kicks',st['sem_kicks'],flush=True)
  except Exception as exc:
   import traceback;row['error']=traceback.format_exc();print(row['error'],flush=True)
  row['seconds']=time.monotonic()-started;report.write_text(json.dumps(out,indent=2)+'\n')
