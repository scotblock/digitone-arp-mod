from pathlib import Path
import sys,os,json,struct,time,traceback,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,dspboot,native,release,sparse
from emu.dtim import Dtims
from emu.longrun import _FastStepper
from emu.snapshot import save
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7,UC_M68K_REG_SR

payload=Path('work/os144/PC_ONLY-atomic-storage-payload.bin').read_bytes()
source=Path('work/os144-emulator-E02-engine/plusdrive.img')
out={'PC_only':True,'cases':[],'limits':['Timer expiry is modeled at native basic-block boundaries with assumed clock costs; no physical timing proof.','Direct MAIN entry with loader-matching boot flags and identical initialized emulator cards, not a physical loader/storage dump.','Cold flash-read shortcut and scoped ISA emulation remain. No host writes satisfy the delay semaphore.']}
dest=Path('outputs/Digitone-E04-PC-resident-deferred-startup-startup.json')
for name,syx,imgfile,cardfile in [('E04_default', 'outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx', 'work/os144/PC_ONLY-atomic-storage-main.bin', 'work/os144-emulator-E02-engine/plusdrive.img'), ('E04_restored', 'outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx', 'work/os144/PC_ONLY-atomic-storage-main.bin', 'work/os144/PC_ONLY-saved-mirror-valid_first.img'), ('E04_disabled', 'outputs/Digitone_OS1.44E04_SCALE_ARP_PC_ONLY.syx', 'work/os144/PC_ONLY-atomic-storage-main.bin', 'work/os144/PC_ONLY-saved-mirror-valid_first.img')]:
 row={'image':name,'events':[],'delay_sem_writes':[],'failure':None};out['cases'].append(row);began=time.monotonic()
 try:
  source=Path(cardfile)
  row['card_source']=cardfile
  root=Path('work/resident-deferred-startup-'+name).resolve();root.mkdir(exist_ok=True)
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
  if name.startswith('E04'):m.ensure(0x47be0000);m.install_isa_patches_scoped(payload[:1784],0x47be0000);m.install_isa_patches_scoped(payload[0x3400:0x3530],0x47be3400)
  row['strict_instruction_checks']={};row['strict_failures']=[];row['initializer_calls']=[];row['restore_events']=[];row['capture_inputs']=[]
  def install_strict(mm,stage):
   mm.install_isa_patches_scoped(payload[0x3000:0x31da],0x47be3000);mm.install_isa_patches_scoped(payload[0x3600:0x36b6],0x47be3600)
   def strict(uc,pc,size,data):
    ins=cfisa.decode(lambda off:int.from_bytes(uc.mem_read(pc+off,2),'big'),pc)
    bad=move_restriction(int.from_bytes(uc.mem_read(pc,2),'big'))
    if bad or ins.flags&(cfisa.ILLEGAL|cfisa.FPU|cfisa.LINEF) or (ins.flags&cfisa.PRIV and not uc.reg_read(UC_M68K_REG_SR)&0x2000):
     row['strict_failures'].append({'pc':hex(pc),'op':ins.op,'reason':bad,'stage':stage});raise AssertionError(row['strict_failures'][-1])
    key=stage+':'+ins.op;row['strict_instruction_checks'][key]=row['strict_instruction_checks'].get(key,0)+1
   for lo,hi in [(0x4029c4b0,0x4029c51d),(0x47be0000,0x47be06f7),(0x47be3400,0x47be352f),(0x47be3000,0x47be31d9),(0x47be3600,0x47be36b5)]:mm.uc.hook_add(UC_HOOK_CODE,strict,begin=lo,end=hi)
   def entering(uc,pc,size,data):
    if name in ['E04_bad_pointer','E04_disabled']:uc.mem_write(0x47be1000,struct.pack('>I',0xffffffff))
   mm.uc.hook_add(UC_HOOK_CODE,entering,begin=0x47be3400,end=0x47be3400)
   def stock(uc,pc,size,data):
    assert int.from_bytes(uc.mem_read(0x47be1010,4),'big')==0
    assert bytes(uc.mem_read(0x47be2000,2080))==bytes(2080)
    row['extra_storage_zero_before_stock']=True
    sp=uc.reg_read(UC_M68K_REG_A7);row['initializer_calls'].append({'stage':stage,'argument':int.from_bytes(uc.mem_read(sp+4,4),'big'),'sr':hex(uc.reg_read(UC_M68K_REG_SR))})
    if name=='E04_post_stock_bad_magic':uc.mem_write(0x47be1004,bytes(4))
   mm.uc.hook_add(UC_HOOK_CODE,stock,begin=0x47be0642,end=0x47be0642)
   def restore(uc,pc,size,data):row['restore_events'].append({'pc':hex(pc),'d0':hex(uc.reg_read(UC_M68K_REG_D0)),'d2':hex(uc.reg_read(UC_M68K_REG_D2))})
   for pc in [0x400a838c,0x400a8402,0x400a83f4,0x400a8410]:mm.uc.hook_add(UC_HOOK_CODE,restore,begin=pc,end=pc)
   def capture(uc,pc,size,data):
    from unicorn.m68k_const import UC_M68K_REG_A3,UC_M68K_REG_D4
    source=uc.reg_read(UC_M68K_REG_A3);track=uc.reg_read(UC_M68K_REG_D4)
    row['capture_inputs'].append({'stage':stage,'source':hex(source),'track':track,'root':bytes(uc.mem_read(source+track*0x3d0+0x3cb,1)).hex(),'scale':bytes(uc.mem_read(source+track*0x3d0+0x3ce,1)).hex()})
   mm.uc.hook_add(UC_HOOK_CODE,capture,begin=0x400947ec,end=0x400947ec)


  input_code=Path('work/os144/PC_ONLY-input-live-overlay.bin').read_bytes()
  m.load(input_code,startup_input_cfg['base']);m.install_isa_patches_scoped(input_code,startup_input_cfg['base'])
  for hook in startup_input_cfg['hooks']:
   assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']
   m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))
  release_code=Path('work/os144/PC_ONLY-release-reset-overlay.bin').read_bytes()
  m.load(release_code,release_startup_cfg['base']);m.install_isa_patches_scoped(release_code,release_startup_cfg['base'])
  for release_hook in release_startup_cfg['hooks']:
   assert bytes(m.uc.mem_read(release_hook['site'],release_hook['length'])).hex()==release_hook['stock']
   m.uc.mem_write(release_hook['site'],bytes.fromhex(release_hook['replacement']))
  for ui_hook in joined_UI_cfg['hooks']:
   assert bytes(m.uc.mem_read(ui_hook['site'],ui_hook['length'])).hex()==ui_hook['stock']
   m.uc.mem_write(ui_hook['site'],bytes.fromhex(ui_hook['replacement']))
  native_defer_code=Path('work/os144/PC_ONLY-resident-deferred-release-overlay.bin').read_bytes()
  m.load(native_defer_code,native_defer_spec['base']);m.install_isa_patches_scoped(native_defer_code,native_defer_spec['base'])
  m.ensure(native_defer_spec['count']);m.uc.mem_write(native_defer_spec['count'],bytes([0xa5])*native_defer_spec['storage_bytes'])
  row['deferred_storage_writes']={};row['deferred_initialization_checks']=[]
  def storage_write(u,access,address,length,value,data):
   if not (0x40000000<=address<0x80000000):return
   canonical=0x40000000+(address-0x40000000)%0x08000000
   if canonical<native_defer_spec['count']+native_defer_spec['storage_bytes'] and canonical+length>native_defer_spec['count']:
    pc=hex(u.reg_read(UC_M68K_REG_PC));record=row['deferred_storage_writes'].setdefault(pc,{'writes':0,'min':hex(canonical),'max':hex(canonical+length)})
    record['writes']+=1;record['min']=hex(min(int(record['min'],16),canonical));record['max']=hex(max(int(record['max'],16),canonical+length))
  for alias in range(8):
   start=native_defer_spec['count']+alias*0x08000000;m.uc.hook_add(UC_HOOK_MEM_WRITE,storage_write,begin=start-64,end=start+native_defer_spec['storage_bytes']+63)
  def initialized_before_seed(u,pc,n,data):
   actual=bytes(u.mem_read(native_defer_spec['count'],native_defer_spec['storage_bytes']));assert actual==bytes(native_defer_spec['storage_bytes'])
   row['deferred_initialization_checks'].append({'pc':hex(pc),'queue_all_zero':True,'phase_before_seed':int.from_bytes(u.mem_read(0x47be2840,4),'big')})
  m.uc.hook_add(UC_HOOK_CODE,initialized_before_seed,begin=0x4029c518,end=0x4029c518)
  for deferred_hook in [h for h in native_defer_spec['hooks'] if h['name']!='completion_dispatch']:
   assert bytes(m.uc.mem_read(deferred_hook['site'],deferred_hook['length'])).hex()==deferred_hook['previous']
   m.uc.mem_write(deferred_hook['site'],bytes.fromhex(deferred_hook['replacement']))





  row['startup_order_events']=[];row['startup_gate_writes']=[];row['producer_entries']=[];row['producer_checkpoints']=[]
  order_stage=['cold']
  def getword(u,a):
   try:return int.from_bytes(u.mem_read(a,4),'big')
   except Exception:return None
  def inputstate(u):
   return {'admission':getword(u,0x47be2840),'READY':getword(u,0x47be1010),'PTR':getword(u,0x47be1000),'receive_gate':getword(u,0x41368d64),'note_gate':getword(u,0x41368d88),'auto_channel':getword(u,0x41368d2c),'test_mode':getword(u,0x402a0e50),'audio_vector':getword(u,0x400002fc),'DIN_vector':getword(u,0x40000270),'panel_vector':getword(u,0x40000268),'DIN_DMA_DADDR':getword(u,0xfc045490),'queue':getword(u,0x419ee22c)}
  row['startup_DIN_injection']=None
  saved_points=set();input_hook_ids={}
  def order(u,pc,n,d):
   row['startup_order_events'].append({'stage':order_stage[0],'pc':hex(pc),'instruction_estimate':done,'SR':hex(u.reg_read(UC_M68K_REG_SR)),**inputstate(u)})
   if order_stage[0]=='cold' and pc in [0x4009d0d8,0x4008d31e,0x4008d3dc,0x4008d3ec] and pc not in saved_points:
    saved_points.add(pc);checkpoint=str(root/('producer-'+hex(pc)+'.snap'))
    save(m,checkpoint,extra={'point':hex(pc),'stage':'cold','state':inputstate(u)})
    row['producer_checkpoints'].append({'pc':hex(pc),'path':checkpoint,'state':inputstate(u)})
   if pc==0x4008d3ec:u.hook_del(input_hook_ids[(order_stage[0],pc)])

   if order_stage[0]=='cold' and pc==0x4009d0d8 and row['startup_DIN_injection'] is None:
    from emu import midi
    channel=getword(u,0x41368d2c)&15
    row['startup_DIN_injection']={'site':hex(pc),'channel':channel,'bytes':bytes([0x90|channel,64,100]).hex(),'before':inputstate(u),'read_index_before':getword(u,0x405285cc),'no_gate_changes':True}
    midi.feed(m,bytes([0x90|channel,64,100]))
    row['startup_DIN_injection']['interrupt_taken']=midi._take(m,156)

  def gatewrite(u,access,a,n,v,d):
   if (a<0x41368d68 and a+n>0x41368d64) or (a<0x41368d8c and a+n>0x41368d88):
    row['startup_gate_writes'].append({'stage':order_stage[0],'pc':hex(u.reg_read(UC_M68K_REG_PC)),'address':hex(a),'bytes':n,'value':v,'instruction_estimate':done,'admission':getword(u,0x47be2840),'READY':getword(u,0x47be1010)})
  def producer(u,pc,n,d):
   if len(row['producer_entries'])<100:row['producer_entries'].append({'stage':order_stage[0],'pc':hex(pc),'instruction_estimate':done,**inputstate(u)})
  def observe_input(mm,stage):
   order_stage[0]=stage
   for at in [0x4000053e,0x40000546,0x4008d300,0x4008d308,0x4008d318,0x4009d0d8,0x400ffed0,0x4009c5d8,0x4009c650,0x4008d31e,0x4008d332,0x4008d3dc,0x4008d7ee,0x4008d814,0x4008d820,0x4008d3ee,0x40019476,0x4001947c,0x4008d3ec]:input_hook_ids[(stage,at)]=mm.uc.hook_add(UC_HOOK_CODE,order,begin=at,end=at)
   mm.uc.hook_add(UC_HOOK_MEM_WRITE,gatewrite,begin=0x41368d20,end=0x41368d8b)
   for at in [0x400eb2d2,0x400eb166,0x400eae5c,0x400eaf48,0x400ff3ec,0x40100252]:mm.uc.hook_add(UC_HOOK_CODE,producer,begin=at,end=at)
  observe_input(m,'cold')


  native_code=Path('work/os144/PC_ONLY-cold-admission-overlay.bin').read_bytes()
  state_code=Path('work/os144/PC_ONLY-persistent-admission.bin').read_bytes()
  m.load(native_code,native_boot_cfg['base']);m.install_isa_patches_scoped(native_code,native_boot_cfg['base'])
  m.load(state_code,native_admission_cfg['base']);m.install_isa_patches_scoped(state_code,native_admission_cfg['base'])
  completion_hook=next(h for h in native_defer_spec['hooks'] if h['name']=='completion_dispatch')
  assert bytes(m.uc.mem_read(completion_hook['site'],completion_hook['length'])).hex()==completion_hook['previous']
  m.uc.mem_write(completion_hook['site'],bytes.fromhex(completion_hook['replacement']))
  for hook in native_boot_cfg['hooks']:
   assert bytes(m.uc.mem_read(hook['site'],hook['length'])).hex()==hook['stock']
   m.uc.mem_write(hook['site'],bytes.fromhex(hook['replacement']))

  row['admission_boundary_events']=[];row['admission_word_writes']=[];row['cold_marker_fixture_only']=False;row['native_boot_helpers_host_loaded']=True
  def boundary(uc,pc,size,data):
   sp=uc.reg_read(UC_M68K_REG_A7)
   try:value=int.from_bytes(uc.mem_read(0x47be2840,4),'big')
   except Exception:value=None
   try:ret=hex(int.from_bytes(uc.mem_read(sp,4),'big'))
   except Exception:ret=None
   event={'pc':hex(pc),'SR':hex(uc.reg_read(UC_M68K_REG_SR)),'SP':hex(sp),'stack_return':ret,'admission_word':hex(value) if value is not None else None,'estimated_instructions':done}
   if pc==0x4029c518:
    assert event['stack_return']=='0x4000053e' and value==0
    assert bytes(uc.mem_read(0x47be0000,len(payload)))[:0x1000]==payload[:0x1000]
    # Marker measures lifetime only. No native admission helper is installed.
    event['native_seed_hook_follows']=True
   elif pc==0x400ffed0:
    event['initializer_argument']=int.from_bytes(uc.mem_read(sp+4,4),'big')
    assert value==0x494e4954 and event['stack_return']=='0x4009c5aa' and event['initializer_argument']==158
   row['admission_boundary_events'].append(event)
  for at in [0x400004e8,0x4029c4b0,0x4029c518,0x40001df4,0x4000053e,0x40000542,0x40000546,0x4009d0d8,0x4009c5ae,0x4009c5a0,0x400ffed0,0x4009c5aa,0x4009c5d8,0x4009c650]:
   m.uc.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
  def wordwrite(uc,access,a,n,v,data):
   if a<0x47be2844 and a+n>0x47be2840:row['admission_word_writes'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(a),'size':n,'value':v})
  m.uc.hook_add(UC_HOOK_MEM_WRITE,wordwrite,begin=0x47be2800,end=0x47be2843)

  install_strict(m,'cold')
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
  if name.startswith('E04'):assert bytes(m.uc.mem_read(0x47be0000,2492))==payload[:2492] and bytes(m.uc.mem_read(0x47be3000,474))==payload[0x3000:0x31da] and bytes(m.uc.mem_read(0x47be3400,304))==payload[0x3400:0x3530]
  row['private_after_cold']=bytes(m.uc.mem_read(0x47be1000,32)).hex()
  row['candidate_after_cold']=bytes(m.uc.mem_read(0x47be1a24,16)).hex()
  save(m,paths.cold,extra={'tasks':{hex(k):v for k,v in st['task_create_hits'].items()},'n':done})
  if m.esdhc.card.path:m.esdhc.card.flush()
  bs._close_card(m);del m,budget
  held={}
  def intro_observe(mm,ev,stage):
   held['ev']=ev
   install_strict(mm,'intro')
   observe_input(mm,'intro')
   if name.startswith('E04'):mm.install_isa_patches_scoped(payload[:1784],0x47be0000);mm.install_isa_patches_scoped(payload[0x3400:0x3530],0x47be3400)
  result=bs.boot_to_ui(paths.syx,paths.cold,budget=400_000_000,fast=True,options={'ddr':0x08000000,'unblock':False,'on_machine':intro_observe})
  row['intro']={'up':result.up,'intro_done':result.intro_done,'mainloop':result.mainloop,'stand_ins':held['ev'].get('stand_ins'),'general_satisfactions':held['ev'].get('satisfied')}
  assert result.up and not held['ev'].get('stand_ins',{}).get('completion_sem',0)
  assert not row['strict_failures'] and len(row['initializer_calls'])==1
  assert row['initializer_calls'][0]['argument']==158
  disabled=name in ['E04_bad_pointer','E04_post_stock_bad_magic','E04_disabled']
  assert row['private_after_cold'][:8]==('00000000' if disabled else '47bccf04')
  assert row['private_after_cold'][32:40]==('00000000' if disabled else '00000001')
  row['passed']=True
 except Exception:row['failure']=traceback.format_exc();row['passed']=False;print(row['failure'],flush=True)
 row['seconds']=time.monotonic()-began;dest.write_text(json.dumps(out,indent=2)+'\n');print('native delay',name,row.get('passed'),row.get('timer_fired'),flush=True)
