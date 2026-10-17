"""Cold OS-entry bootstrap -> native initialization -> UI -> playback. PC only."""
import pathlib,shutil,json,struct,time,traceback,os
source=pathlib.Path('work/test-native-arp-overlays.py').read_text()
exec(source.split('def run(mode):')[0])
startup=json.loads(pathlib.Path('work/native-overlay-startup.json').read_text());INIT=startup['initializer']
oldpaths=paths
ROOT=pathlib.Path('work/indexed-loader-derived-arp-emulator').resolve();ROOT.mkdir(parents=True,exist_ok=True)
paths=ExperimentalPaths(str(ROOT),SYX.name,oldpaths.devices_dir)
for dest,src in [(paths.sections,oldpaths.sections),(paths.overlay,oldpaths.overlay)]:
 shutil.copytree(src,dest,dirs_exist_ok=True)
# Copy the completed synthetic card; the stock snapshots/card are not advanced.
if not pathlib.Path(paths.card).exists():shutil.copyfile(oldpaths.card,paths.card)
pathlib.Path(paths.snapdir).mkdir(parents=True,exist_ok=True);pathlib.Path(paths.logs).mkdir(parents=True,exist_ok=True)
os.environ.update(paths.env())
STAGE=base+len(stock)
# Rebuild the early copier using the corrected native code length.
a=bytearray()
def emit(h):a.extend(bytes.fromhex(h))
emit('41f9'+u32(STAGE+0x100).hex()+'43f9'+u32(RAM).hex()+'203c'+u32(len(blob)//4).hex())
emit('22d853806600fffa')
emit('43f9'+u32(PTR).hex()+'203c'+u32(0xb74//4).hex());emit('720022c153806600fffa')
emit('23fc'+u32(BSS-0x14100).hex()+u32(PTR).hex())
for addr,value in [(BSS,0x534c4332),(BSS+4,2),(BSS+8,0xb70)]:emit('23fc'+u32(value).hex()+u32(addr).hex())
emit('4ef940001df4');boot=bytes(a);assert len(boot)<=0x100 and len(blob)%4==0
OUT=pathlib.Path('outputs/Digitone-native-cold-arp-results.json')
report.update(startup={'source':hex(STAGE+0x100),'bootstrap':hex(STAGE),'initializer':hex(INIT),'copy_longs':len(blob)//4,'bootstrap_bytes':len(boot),'stages':[],'events':[],'failure':None,'starts_at':'Executed full loader, retaining the same machine into application initialization'},runs=[])
machines=[];began=time.monotonic()
def persist():
 report['elapsed_seconds']=round(time.monotonic()-began,1);OUT.write_text(json.dumps(report,indent=2))
def stage_install(m,ev,stage):
 uc=m.uc;rec={'stage':stage,'hits':{},'unexpected_writes':[],'copier_writes':0,'initializer_writes':0,'helper_writes':0,'initial_ready':None,'entry_flags':None};report['startup']['stages'].append(rec);machines.append((m,rec))
 m.ensure(RAM);m.ensure(STAGE);m.ensure(0x4199d590)
 if stage=='ladder':
  assert m is LOADER_MACHINE and cpu_state(m)==LOADER_STATE
  assert bytes(uc.mem_read(base,len(LOADER_MAIN)))==LOADER_MAIN
  assert bytes(uc.mem_read(RAM,0x20000))==bytes(0x20000)
  rec['entry_flags']=hex(LOADER_RESULT.boot_flags)+' from executed loader'
  report['loader']={'entry':hex(LOADER_RESULT.reached),'main_matches':LOADER_RESULT.main_os_matches,'flags':hex(LOADER_RESULT.boot_flags),'controls':{hex(k):hex(v) for k,v in LOADER_RESULT.m.ctlregs.items()},'same_machine_into_initializer':True,'hooks_removed':len(LOADER_HANDLES),'flash_writes':LOADER_RESULT.flash_writes,'image_sha256':hashlib.sha256(LOADER_MAIN).hexdigest(),'image_bytes':len(LOADER_MAIN),'model_mmio_changes':{hex(k):{'loader':hex(LOADER_MMIO.get(k,0)),'application':hex(v)} for k,v in m.mmio.items() if LOADER_MMIO.get(k)!=v},'limits':['Serial reset hardware represented by loaded bootstrap SRAM.','Bootstrap device hooks replaced by application device models at MAIN entry; CPU, control, SRAM and DDR state retained.','Intro, settle and playback use guest snapshots in fresh engines; this is guest-state continuity, not one engine throughout.','Flash-read HLE and storage/semaphore/timer shortcuts remain modeled.','Playback changes root/scale in a labeled test fixture; it does not prove natural context capture.','Physical cache, DMA and DDR coherence remain unverified.']}
 else:
  assert bytes(uc.mem_read(RAM,len(blob)))==blob,'copied code not preserved'
  assert rd(uc,PTR)==BSS-0x14100 and rd(uc,BSS+12)==1,'initializer readiness not preserved'
 rec['initial_ready']=hex(rd(uc,BSS+12))
 m.install_isa_patches_scoped(blob,RAM);m.install_isa_patches_scoped(boot,STAGE)
 def hit(uc,pc,n,d):
  label={STAGE:'copier_entry',0x4000053e:'copier_return',INIT:'initializer_entry',0x400f050e:'stock_initializer_body',0x4009bcc4:'initializer_caller_return'}[pc]
  rec['hits'][label]=rec['hits'].get(label,0)+1
  report['startup']['events'].append({'stage':stage,'label':label,'pc':hex(pc),'ready':hex(rd(uc,BSS+12)),'SR':hex(uc.reg_read(UC_M68K_REG_SR)),'stock_owner':hex(rd(uc,0x4199d590))})
  if pc==0x4000053e:assert bytes(uc.mem_read(RAM,len(blob)))==blob and rd(uc,BSS+12)==0
  if pc==0x400f050e:assert rd(uc,BSS+12)==0 and uc.reg_read(UC_M68K_REG_SR)&0x0700==0x0700
  if pc==0x4009bcc4:assert rd(uc,BSS+12)==1
  persist()
 for pc in [STAGE,0x4000053e,INIT,0x400f050e,0x4009bcc4]:uc.hook_add(UC_HOOK_CODE,hit,begin=pc,end=pc)
 def writes(uc,access,addr,n,value,d):
  physical=0x40000000+(addr-0x40000000)%DDR
  if not (physical<RAM+0x20000 and RAM<physical+n):return
  pc=uc.reg_read(UC_M68K_REG_PC)
  if STAGE<=pc<STAGE+len(boot) and ((RAM<=physical and physical+n<=RAM+len(blob)) or (PTR<=physical and physical+n<=BSS+0xb70)):
   rec['copier_writes']+=1;return
  if PTR<=physical and physical+n<=BSS+0xb70:
   if RAM<=pc<RAM+len(blob):rec['helper_writes']+=1;return
   if 0x400ec284<=pc<0x400ec400 and rd(uc,BSS+12)==0 and uc.reg_read(UC_M68K_REG_SR)&0x0700==0x0700:
    rec['initializer_writes']+=1;return
  rec['unexpected_writes'].append({'pc':hex(pc),'address':hex(addr),'size':n});uc.emu_stop()
 for k in range(8):uc.hook_add(UC_HOOK_MEM_WRITE,writes,begin=RAM+k*DDR-64,end=RAM+k*DDR+0x20000+63)
def verify_stages():
 for m,rec in machines:
  uc=m.uc;rec['code_intact']=bytes(uc.mem_read(RAM,len(blob)))==blob;rec['ready']=rd(uc,BSS+12);owner=rd(uc,0x4199d590);rec['stock_owner']=hex(owner)
  rec['stock_pool_links_valid']=bool(owner) and all(rd(uc,owner+i*0x504+16)==(owner+(i+1)*0x504 if i<63 else 0) for i in range(64))
  rec['guards_intact']=bytes(uc.mem_read(RAM+len(blob),PTR-RAM-len(blob)))==bytes([0])*(PTR-RAM-len(blob)) and bytes(uc.mem_read(BSS+0xb70,RAM+0x20000-BSS-0xb70))==bytes([0])*(RAM+0x20000-BSS-0xb70)
  assert rec['code_intact'] and rec['ready']==1 and rec['guards_intact'] and not rec['unexpected_writes'],rec
 persist()
def progress(event):
 if event.kind in ['done','note'] or time.monotonic()-getattr(progress,'last',0)>12:
  print(event.step,event.kind,event.text or getattr(event,'done',None),flush=True);progress.last=time.monotonic()
def cancel():return time.monotonic()-began>900
try:
 options={'ddr':DDR,'on_machine':stage_install}
 cold=bs.cold_boot(paths,progress=progress,cancel=cancel,chunk=2_000_000,limit=300_000_000,options=options)
 report['startup']['cold_result']=cold;verify_stages()
 intro=bs.boot_to_ui(str(SYX),paths.cold,out=paths.gui_raw,progress=progress,cancel=cancel,fast=True,options=options,**bs.INTRO)
 assert intro.up and intro.saved;report['startup']['intro_result']=str(intro);verify_stages()
 settle=bs.settle_ui(str(SYX),paths.gui_raw,out=paths.gui,progress=progress,cancel=cancel,fast=True,fast_idle=True,options=options,**bs.SETTLE)
 assert settle.settled_at is not None and settle.saved;report['startup']['settle_result']=str(settle);verify_stages()
 # Playback restores only the code/header created by actual startup instructions.
 body=source[source.index('def run(mode):'):source.index('\ntry:\n if os.environ')]
 body=body.replace("uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74))\n   uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))","assert bytes(uc.mem_read(RAM,len(blob)))==blob and rd(uc,BSS+12)==1")
 body=body.replace("original==stock[pc-base:pc-base+length]","original==bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((length-6)//2)")
 body=body.replace("uc.mem_write(pc,bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((length-6)//2))","# Restored hooks must already match; do not reinstall them.")
 exec(compile(body,'cold-start-playback','exec'))
 run('scale-fixture')
 assert report['runs'][0]['halted'] is None and all(report['runs'][0]['checks'].values())
 assert report['runs'][0]['quantize_calls'],'no real arp quantizer path reached'
 report['firmware_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();assert report['firmware_before']==report['firmware_after']
 report['passed']=True
except BaseException as exc:
 report['startup']['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(report['startup']['failure']['traceback'],flush=True);report['passed']=False
finally:persist()
