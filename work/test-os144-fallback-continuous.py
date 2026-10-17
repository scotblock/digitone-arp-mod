from pathlib import Path
import sys,os,json,time,struct,hashlib,traceback,collections
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
# Reuse the tested assembler without running its captured-state cases.
exec(Path('work/test-os144-startup-fallback-design.py').read_text().split("\nout={'PC_only'")[0])
from emu import bootstrap as bs,release
from emu.session import Session
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
mode=sys.argv[1];assert mode in ['valid','bad_magic','bad_pointer']
syx=Path('outputs/Digitone_OS1.44E03_SCALE_ARP_PC_ONLY.syx').resolve()
root=Path('work/os144-fallback-prepared-'+mode).resolve();root.mkdir(exist_ok=True)
devices=Path('work/upstream/digiemu/devices').resolve()
class Paths(bs.FirmwarePaths):
 @property
 def syx(self):return str(syx)
paths=Paths(str(root),syx.name,str(devices))
if not Path(paths.card).exists():
 from emu import sparse
 source=Path('work/os144-emulator-E02-engine/plusdrive.img')
 assert not bs.check_card(str(source),ekfs=False)
 with source.open('rb') as src,open(paths.card,'wb') as dst:
  sparse.make_sparse(dst);sparse.extend(dst,source.stat().st_size)
  while chunk:=src.read(1024*1024):
   offset=src.tell()-len(chunk)
   if chunk.strip(b'\0'):dst.seek(offset);dst.write(chunk)
rel=release.identify_release(str(syx),str(devices));release.write_device_overlay(rel,paths.overlay,str(devices));os.environ.update(paths.env())
report=Path('outputs/Digitone-OS1.44-fallback-continuous-'+mode+'.json')
r={'PC_only':True,'firmware_unchanged':True,'mode':mode,'entry':hex(ENTRY),'startup_entries':[],'tasks':[],'heap_writes':[],'dma_descriptors':{},'reservation_writers':{},'top_stack_min_write':None,'stages':[],'failure':None}
start=time.monotonic();hits=collections.Counter();port=json.loads(Path('work/os144/helper-port.json').read_text())
def persist():
 r['seconds']=time.monotonic()-start;report.write_text(json.dumps(r,indent=2))
def progress(ev):
 if ev.text:print(ev.step,ev.text,flush=True)
 persist()
def install(m,ev,stage):
 uc=m.uc;r['stages'].append(stage)
 m.ensure(ENTRY);m.load(code,ENTRY);m.install_isa_patches_scoped(code,ENTRY)
 uc.mem_write(0x400ffed0,bytes.fromhex('4ef9')+u32(ENTRY))
 def entering(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7)
  r['startup_entries'].append({'stage':stage,'arg':int.from_bytes(uc.mem_read(sp+4,4),'big'),'pointer_before':hex(int.from_bytes(uc.mem_read(PTR,4),'big'))})
  if mode=='bad_magic':uc.mem_write(BSS,u32(0))
  if mode=='bad_pointer':uc.mem_write(PTR,u32(0xffffffff))
 uc.hook_add(UC_HOOK_CODE,entering,begin=ENTRY,end=ENTRY)
 def task(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);tcb,entry,prio,stack,size=struct.unpack('>5I',uc.mem_read(sp+4,20))
  item={'stage':stage,'tcb':hex(tcb),'entry':hex(entry),'priority':prio,'stack_base':hex(stack),'bytes':size,'end':hex(stack+size)}
  item['overlaps_reservation']=stack<0x47c00000 and stack+size>RAM;r['tasks'].append(item)
 uc.hook_add(UC_HOOK_CODE,task,begin=0x4000170c,end=0x4000170c)
 def heap(uc,access,address,size,value,d):
  if address==0x40240070:return
  r['heap_writes'].append({'stage':stage,'pc':hex(uc.reg_read(UC_M68K_REG_PC)),'address':hex(address),'size':size,'value':hex(value)})
 uc.hook_add(UC_HOOK_MEM_WRITE,heap,begin=0x40240058,end=0x40240073)
 def dma(uc,access,address,size,value,d):
  if (address-0xfc045000)%32 not in [30,31]:return
  channel=(address-0xfc045000)//32
  values=struct.unpack('>IHhIIIHhIHH',uc.mem_read(0xfc045000+32*channel,32))
  key=str(channel)+':'+','.join(hex(x&0xffffffff) for x in values)
  if key not in r['dma_descriptors']:
   src,attr,soff,nbytes,slast,dst,citer,doff,dlast,biter,csr=values
   count=(biter&0x1ff) if biter&0x8000 else biter&0x7fff
   item={'stage':stage,'channel':channel,'source':hex(src),'destination':hex(dst),'nbytes':nbytes,'iterations':count,'source_stride':soff,'destination_stride':doff,'attr':hex(attr),'csr_written':hex(value)}
   # Conservative envelopes; modulo buffers occupy their entire wrap span.
   ranges=[]
   for addr,stride,mod in [(src,soff,(attr>>11)&31),(dst,doff,(attr>>3)&31)]:
    width=1<<((attr>>8)&7) if addr==src else 1<<(attr&7)
    if mod:lo=addr&~((1<<mod)-1);hi=lo+(1<<mod)
    else:
     delta=(max(1,count)*max(1,nbytes)//max(1,width)-1)*stride
     lo=min(addr,addr+delta);hi=max(addr,addr+delta)+max(width,nbytes)
    physical=0x40000000+(lo-0x40000000)%0x08000000 if 0x40000000<=lo<0x80000000 else lo
    overlaps=physical<0x47c00000 and physical+(hi-lo)>RAM
    ranges.append({'start':hex(lo),'end':hex(hi),'canonical_start':hex(physical),'overlaps_reservation':overlaps})
   item['envelopes']=ranges;r['dma_descriptors'][key]=item
 uc.hook_add(UC_HOOK_MEM_WRITE,dma,begin=0xfc045000,end=0xfc0457ff)
 def software_start(uc,access,address,size,value,d):
  channel=value&63
  dma(uc,access,0xfc045000+channel*32+30,2,1,d)
 uc.hook_add(UC_HOOK_MEM_WRITE,software_start,begin=0xfc04401e,end=0xfc04401e)
 def writes(uc,access,address,size,value,d):
  canonical=0x40000000+(address-0x40000000)%0x08000000;pc=uc.reg_read(UC_M68K_REG_PC)
  if canonical<0x47c00000:
   key=hex(pc);item=r['reservation_writers'].setdefault(key,{'count':0,'min':hex(canonical),'max':hex(canonical+size),'stage':stage});item['count']+=1;item['min']=hex(min(int(item['min'],16),canonical));item['max']=hex(max(int(item['max'],16),canonical+size))
  elif canonical>=0x47c00000:
   r['top_stack_min_write']=hex(min(int(r['top_stack_min_write'],16) if r['top_stack_min_write'] else 0x48000000,canonical))
 for alias in range(8):uc.hook_add(UC_HOOK_MEM_WRITE,writes,begin=RAM+alias*0x08000000,end=0x47ffffff+alias*0x08000000)
 for name in ['producer_capture','allocate_clear','pitch_hook','copy','first_copy']:
  address=port['layout'][name]['address']
  uc.hook_add(UC_HOOK_CODE,lambda uc,pc,n,d,name=name:hits.update([name]),begin=address,end=address)
try:
 snap=bs.first_run(paths,progress=progress,options={'ddr':0x08000000,'on_machine':install});r['snapshot']=snap
 s=Session(snap,syx=str(syx),ddr=0x08000000,on_machine=lambda s:install(s.m,s.ev,'playback'))
 try:
  uc=s.m.uc;r['pointer_at_UI']=hex(int.from_bytes(uc.mem_read(PTR,4),'big'));r['header_at_UI']=list(struct.unpack('>4I',uc.mem_read(BSS,16)))
  assert r['startup_entries'] and all(x['arg']==158 for x in r['startup_entries'])
  assert int(r['pointer_at_UI'],16)==(EXPECTED if mode=='valid' else 0)
  for track in range(4):
   uc.mem_write(0x40813531+track*0x3d0+0x3cb,bytes([61]));uc.mem_write(0x40813531+track*0x3d0+0x3ce,bytes([0]))
  pitches=[]
  s.at(0x4009e890,lambda uc,pc,n,d:pitches.append(uc.reg_read(UC_M68K_REG_D6)))
  s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
  s.press(s.code('PTN'));s.run_ms(100);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(300)
  s.tap(s.code('PLAY'),hold_ms=100,after_ms=1500)
  s.tap(s.code('STOP'),hold_ms=100,after_ms=200)
  r.update(halted=s.halted,audio_bytes=len(s.pcm),audio_sha256=hashlib.sha256(s.pcm).hexdigest(),pitches=pitches,helper_hits=dict(hits),pointer_after_playback=hex(int.from_bytes(uc.mem_read(PTR,4),'big')),heap_at_end={hex(a):hex(int.from_bytes(uc.mem_read(a,4),'big')) for a in range(0x40240058,0x40240074,4)})
  assert s.halted is None and pitches and len(s.pcm)>0 and hits['pitch_hook']>0
  assert r['pointer_after_playback']==r['pointer_at_UI']
  assert not any(t['overlaps_reservation'] for t in r['tasks'])
  assert not any(e['overlaps_reservation'] for desc in r['dma_descriptors'].values() for e in desc['envelopes'])
  r['passed']=True
 finally:s.close()
except BaseException:r['passed']=False;r['failure']=traceback.format_exc();print(r['failure'],flush=True)
finally:persist()
print('RESULT',mode,r.get('passed'),r['seconds'],flush=True)
if not r.get('passed'):raise SystemExit(1)
