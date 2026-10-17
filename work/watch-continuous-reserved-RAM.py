"""Stock OS continuous-engine ownership probe. No firmware overlays or hardware I/O."""
import sys,pathlib,os,json,time,hashlib,struct,traceback,collections
sys.path[:0]=[str(pathlib.Path('work/emulator-deps').resolve()),str(pathlib.Path('work/upstream/digiemu').resolve())]
from unicorn import UC_HOOK_MEM_WRITE,UC_HOOK_CODE,UC_HOOK_BLOCK
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_A7
from emu import bootstrap as bs,symbols
ROOT=pathlib.Path('work/continuous-emulator').resolve();ROOT.mkdir(parents=True,exist_ok=True)
SYX=pathlib.Path('inputs/Digitone_and_Digitone_Keys_OS1.42.syx')
RAM,RAMEND,OCCUPIED=0x47be0000,0x47c00000,0x47be1b74
DDR=0x08000000
PATTERN=bytes(((i*73+19)^(i>>8))&255 for i in range(RAMEND-RAM));DIGEST=hashlib.sha256(PATTERN).hexdigest()
OUT=pathlib.Path('outputs/Digitone-continuous-RAM-watch-results.json')
start=time.monotonic();watches=[];events=[];failure=None;playback=None
prior=pathlib.Path('outputs/Digitone-continuous-RAM-watch-initial-results.json')
if os.environ.get('DIGITONE_CONTINUE_WATCH')=='1':
 old=json.loads(OUT.read_text());prior.write_text(json.dumps(old,indent=2))
 for record in old['stage_watches']:
  record['run']='initial detailed stack sample';watches.append({'m':None,'ev':{},'result':record})
class ExperimentalPaths(bs.FirmwarePaths):
 @property
 def syx(self):return str(SYX)
paths=ExperimentalPaths(str(ROOT),SYX.name,str(pathlib.Path('work/upstream/digiemu/devices').resolve()))
# Local experimental identity only: exact user-file hash; no upstream support claim.
overlay=pathlib.Path(paths.overlay);overlay.mkdir(exist_ok=True)
dev=pathlib.Path('work/upstream/digiemu/devices/digitone.toml').read_text()
dev=dev.replace('version = "1.43"','version = "1.42"',1).replace('c5a54cc05b921f2e4bd814834c5365c2a5aa01d7772a9a2961fac1c3095bf9aa',hashlib.sha256(SYX.read_bytes()).hexdigest(),1)
(overlay/'digitone-experimental-1.42.toml').write_text('# LOCAL EXPERIMENTAL PROFILE: not upstream-supported OS 1.42.\n'+dev)
os.environ.update(paths.env())
profile=symbols.resolve(pathlib.Path(paths.main_img).read_bytes())
def canonical(a):return 0x40000000+(a-0x40000000)%DDR if 0x40000000<=a<0x80000000 else a
def overlaps(a,n):
 if n<=0 or a>=0x80000000 or a+n<=0x40000000:return False
 for k in range(8):
  lo=RAM+k*DDR
  if a<lo+RAMEND-RAM and lo<a+n:return True
 return False
def persist():
 report={'upstream_commit':'24a1dcfbb53de52c42b0d3f2f2a2f5029873f0d2','experimental_OS1.42_profile':True,'region':[hex(RAM),hex(RAMEND)],'occupied_end':hex(OCCUPIED),'sentinel_sha256':DIGEST,'firmware_modified':False,'firmware_sha256':hashlib.sha256(SYX.read_bytes()).hexdigest(),'elapsed_seconds':round(time.monotonic()-start,1),'stage_watches':[w['result'] for w in watches],'progress':events,'failure':failure,'playback':playback,'limits':['Stock firmware only: reserved interval is a sentinel, not an installed mod.','App bootstrap argument supplied as 0x00140000; pre-OS bootstrap not executed.','Upstream flash-read HLE, completion-semaphore stand-in, idle reschedules, and later forced wait completion affect ordering.','Initial SP sampled at every 64th basic-block entry and scheduler switch; continued SP trace uses scheduler switches only. Transient unsampled minima remain unproven.','Guest writes and host writes through this engine mem_write API monitored; native DMA writes may bypass callbacks, so persistent effects are checked by full-region digests at progress boundaries. Physical DMA/cache and unmodelled devices remain unproven.','Snapshot stage continuity is guest-state continuity, not one continuously running engine.','Detailed initial settle was time-bounded; the lighter continuation replays from the same saved post-intro state, not from its cancelled instruction.','A successful finite session does not prove global exclusive ownership.']}
 OUT.write_text(json.dumps(report,indent=2))
def install(m,ev,stage):
 result={'stage':stage,'run':'lighter continuation' if os.environ.get('DIGITONE_CONTINUE_WATCH')=='1' else 'initial detailed stack sample','guest_region_writes':[],'host_region_writes':[],'stack_samples':0,'blocks':0,'stack_ranges':{},'tasks':{},'sentinel_intact':None,'entry_boot_flags':None}
 if watches:result['tasks']=json.loads(json.dumps(watches[-1]['result']['tasks']))
 w={'m':m,'result':result,'ev':ev};watches.append(w)
 m.ensure(RAM)
 if stage=='ladder':
  m.uc.mem_write(RAM,PATTERN)
  sp=m.uc.reg_read(UC_M68K_REG_A7);m.ensure(sp+4);m.uc.mem_write(sp+4,struct.pack('>I',0x00140000));result['entry_boot_flags']='0x00140000 supplied at entry'
 else:
  assert bytes(m.uc.mem_read(RAM,len(PATTERN)))==PATTERN,'sentinel not preserved across snapshot restore'
 original_host_write=m.uc.mem_write
 def host_write(a,data):
  if overlaps(a,len(data)):
   result['host_region_writes'].append({'pc':hex(m.uc.reg_read(UC_M68K_REG_PC)),'address':hex(a),'length':len(data)});persist()
  return original_host_write(a,data)
 m.uc.mem_write=host_write
 def guest_write(uc,access,a,n,v,data):
  if not overlaps(a,n):return
  result['guest_region_writes'].append({'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(a),'physical':hex(canonical(a)),'size':n,'value':hex(v&((1<<(8*n))-1))});persist();uc.emu_stop()
 for k in range(8):
  lo=RAM+k*DDR
  # Unicorn routes by the starting address. Include a margin for stores
  # beginning outside the interval, then filter by full access overlap.
  m.uc.hook_add(UC_HOOK_MEM_WRITE,guest_write,begin=lo-64,end=lo+RAMEND-RAM+63)
 # Watch task_create itself; stack argument is a lower bound and size is
 # rounded down to a multiple of four by the stock routine at 40001712.
 def created(uc,a,n,data):
  sp=uc.reg_read(UC_M68K_REG_A7)
  tcb,entry,prio,stack,size=struct.unpack('>IIIII',uc.mem_read(sp+4,20));size&=~3
  result['tasks'][hex(tcb)]={'entry':hex(entry),'priority':prio,'stack_low':hex(stack),'stack_end':hex(stack+size),'size':size,'physical_overlap':overlaps(stack,size)}
 m.uc.hook_add(UC_HOOK_CODE,created,begin=profile.task_create,end=profile.task_create)
 def sample(uc,pc):
  sp=uc.reg_read(UC_M68K_REG_A7)
  try:tcb=struct.unpack('>I',uc.mem_read(profile.current_tcb,4))[0]
  except Exception:tcb=0
  # Attribute using physical stack interval as TCB changes during a switch.
  matched=[key for key,task in result['tasks'].items() if int(task['stack_low'],16)<=canonical(sp)<int(task['stack_end'],16)]
  key=matched[0] if len(matched)==1 else 'unattributed:'+hex(tcb)
  r=result['stack_ranges'].setdefault(key,{'minimum':hex(sp),'maximum':hex(sp),'minimum_pc':hex(pc),'samples':0})
  if sp<int(r['minimum'],16):r['minimum']=hex(sp);r['minimum_pc']=hex(pc)
  if sp>int(r['maximum'],16):r['maximum']=hex(sp)
  r['samples']+=1;result['stack_samples']+=1
  if RAM<=canonical(sp)<RAMEND:raise AssertionError('observed SP inside candidate region')
 def block(uc,a,n,data):
  result['blocks']+=1
  if result['blocks']%64==0:sample(uc,a)
 if os.environ.get('DIGITONE_CONTINUE_WATCH')!='1':m.uc.hook_add(UC_HOOK_BLOCK,block)
 m.uc.hook_add(UC_HOOK_CODE,lambda uc,a,n,d:sample(uc,a),begin=profile.ctx_switch_load,end=profile.ctx_switch_load)
 persist()
def refresh():
 for w in watches:
  if w['m'] is None:continue
  try:w['result']['sentinel_intact']=hashlib.sha256(bytes(w['m'].uc.mem_read(RAM,len(PATTERN)))).hexdigest()==DIGEST
  except Exception:pass
  if isinstance(w['ev'],dict):
   w['result']['model_counters']={key:w['ev'].get(key) for key in ['sem_kicks','depack_clamps','satisfied'] if key in w['ev']}
   if 'stand_ins' in w['ev']:w['result']['stand_ins']=dict(w['ev']['stand_ins'])
def progress(event):
 refresh()
 events.append({'step':event.step,'kind':event.kind,'text':event.text,'done':getattr(event,'done',None),'elapsed':round(time.monotonic()-start,1)})
 if event.kind in ['done','note'] or (event.kind=='tick' and time.monotonic()-getattr(progress,'last',0)>8):
  print(event.step,event.kind,event.text or getattr(event,'done',None),flush=True);progress.last=time.monotonic()
 persist()
 if any(w['result']['guest_region_writes'] or w['result']['host_region_writes'] or w['result']['sentinel_intact'] is False for w in watches):raise RuntimeError('reserved-region intrusion detected')
def cancel():return time.monotonic()-start>900
# Bound a first compatibility run; counts are counted when no native budget.
bs.COLD.update(chunk=2_000_000,max=300_000_000)
try:
 gui=bs.first_run(paths,progress=progress,cancel=cancel,options={'ddr':DDR,'on_machine':install})
 from emu.session import Session
 session=Session(gui,syx=str(SYX),ddr=DDR,on_machine=lambda session:install(session.m,session.ev,'playback'))
 try:
  session.run_ms(250);session.press(11);session.run_ms(1500);session.release(11);session.run_ms(250);session.press(12);session.run_ms(100);session.release(12)
  playback={'emulated_ms':session.ms,'frames':len(session.frames),'audio_bytes':len(session.pcm),'halted':session.halted,'inputs':session.inputs}
 finally:session.close()
except BaseException as exc:
 failure={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print('STOP',failure['type'],failure['message'],flush=True)
finally:
 refresh();persist();print('Saved',str(OUT),flush=True)
