from pathlib import Path
exec(Path('work/probe-PC-startup-settled-MIDI.py').read_text().split('\nfor c in startup')[0])
from emu import edma_sw
from unicorn import UC_HOOK_MEM_WRITE
import hashlib,collections
spec=json.loads(Path('work/os144/PC_ONLY-resident-deferred-release-overlay.json').read_text());start=json.loads(Path('outputs/Digitone-E04-PC-resident-deferred-startup-startup.json').read_text());case=next(c for c in start['cases'] if c['image']=='E04_restored');root=Path(case['ui_snapshot']).parents[2];paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
LO=spec['count'];HI=LO+spec['storage_bytes'];report={'PC_only':True,'guest_writers':{},'host_queue_writes':[],'bulk_calls':collections.Counter(),'bulk_overlaps':[],'DMA':{},'copier_or_reset_entries':[],'marks':[],'failure':None};s=None
# Use all DDR aliases and split neither wrap nor long interval silently.
def overlaps(a,n):return n>0 and any(a<HI+k*0x08000000 and a+n>LO+k*0x08000000 for k in range(8))
def descriptor(ch,raw,origin):
 td=struct.unpack(edma_sw.TCD_FMT,raw);src,attr,soff,nbytes,slast,dst,citer,doff,dlast,biter,csr=td;count=max(edma_sw.iteration_count(citer),edma_sw.iteration_count(biter))
 if not nbytes or not count:return
 key=str(ch)+':'+raw.hex()
 if key in report['DMA']:return
 mod=(attr>>3)&31;width=1<<(attr&7);unknown=[]
 if nbytes&0xc0000000:unknown.append('minor-loop offset encoding not decoded')
 if mod:low=dst&~((1<<mod)-1);high=low+(1<<mod)
 else:
  moves=count*((nbytes+width-1)//width);delta=max(0,moves-1)*doff;low=min(dst,dst+delta);high=max(dst,dst+delta)+max(width,nbytes)
 if low<0 or high>0x100000000:unknown.append('32-bit wrap not decoded')
 row={'channel':ch,'origin':origin,'destination':hex(dst),'low':hex(low),'high':hex(high),'nbytes':nbytes,'iterations':count,'modulo_bits':mod,'scatter_gather':bool(csr&16),'next_descriptor':hex(dlast),'unknown':unknown,'overlaps_queue':overlaps(low,high-low)};report['DMA'][key]=row
 # Scatter-gather is tracked as an explicit unfinished edge here. Descriptor
 # callbacks inspect concrete runtime TCDs; no nonexistent chain is invented.
try:
 def install(s):
  for a,n in [(0x47be0000,1784),(0x47be3000,474),(0x47be3400,304),(0x47be3600,182),(0x47fa0000,332),(0x47fa0300,280),(0x47fa0600,492),(0x47fa0900,594),(spec['base'],spec['bytes'])]:s.m.install_isa_patches_scoped(bytes(s.m.uc.mem_read(a,n)),a)
  u=s.m.uc
  def written(u,access,a,n,v,d):
   if overlaps(a,n):
    pc=u.reg_read(UC_M68K_REG_PC);report['guest_writers'][hex(pc)]=report['guest_writers'].get(hex(pc),0)+1;assert spec['base']<=pc<spec['base']+spec['bytes']
  for k in range(8):u.hook_add(UC_HOOK_MEM_WRITE,written,begin=LO+k*0x08000000-64,end=HI+k*0x08000000+63)
  old=u.mem_write
  def host_write(a,data):
   if overlaps(a,len(data)):report['host_queue_writes'].append({'address':hex(a),'bytes':len(data),'pc':hex(u.reg_read(UC_M68K_REG_PC))})
   return old(a,data)
  u.mem_write=host_write
  for entry,label in [(0x400fbad8,'memcpy'),(0x400fbb20,'memset')]:
   def bulk(u,pc,n,d,label=label):
    sp=u.reg_read(UC_M68K_REG_A7);dest,other,size=struct.unpack('>III',u.mem_read(sp+4,12));report['bulk_calls'][label]+=1
    if overlaps(dest,size):report['bulk_overlaps'].append({'kind':label,'destination':hex(dest),'bytes':size,'pc':hex(pc)})
   s.at(entry,bulk)
  for ch in range(64):descriptor(ch,bytes(u.mem_read(0xfc045000+ch*32,32)),'initial live configuration')
  def sample(u,access,a,n,v,d):
   ch=(a-0xfc045000)//32
   if 0<=ch<64:
    raw=bytearray(u.mem_read(0xfc045000+ch*32,32));off=a-(0xfc045000+ch*32)
    if off+n<=32:raw[off:off+n]=(v&((1<<(n*8))-1)).to_bytes(n,'big');descriptor(ch,bytes(raw),'guest TCD write including incoming value')
  u.hook_add(UC_HOOK_MEM_WRITE,sample,begin=0xfc045000,end=0xfc0457ff)
  bank=s.ev.get('edma_sw_bank')
  if bank:
   for ch in bank.channels.values():
    previous=ch._transfer
    def transfer(u,ensure=True,ch=ch,previous=previous):descriptor(ch.channel,bytes(u.mem_read(0xfc045000+ch.channel*32,32)),'software transfer entry');return previous(u,ensure)
    ch._transfer=transfer
  for pc in [0x400004e8,0x40000538,0x4029c4b0]:s.at(pc,lambda u,pc,n,d:report['copier_or_reset_entries'].append(hex(pc)))
 s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install);s.run_ms(200);u=s.m.uc;initial=bytes(u.mem_read(LO,spec['storage_bytes']));assert initial==bytes(spec['storage_bytes'])
 for key in ['KEYBOARD','T1','1','T2','5','PLAY']:s.tap(s.code(key),hold_ms=100,after_ms=200)
 for key in ['1','3','5','7']:s.press(s.code(key));s.run_ms(100)
 s.run_ms(1500)
 for key in ['1','3','5','7']:s.release(s.code(key));s.run_ms(100)
 mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources+=(mi,);ch=rd(u,0x41368d2c)&15
 def send(data):
  for i,b in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,b)
  mi.received+=len(data);s.run_ms(200)
 send([0xb0|ch,64,127]);send([0x90|ch,60,100]);send([0x90|ch,64,100]);send([0x80|ch,60,0]);send([0x80|ch,64,0]);send([0xb0|ch,64,0])
 before=rd(u,0x4138f214);s.press(s.code('PTN'));s.run_ms(50);s.tap(s.code('2'),hold_ms=100,after_ms=100);s.release(s.code('PTN'));s.run_ms(2000);after=rd(u,0x4138f214)
 s.tap(s.code('STOP'),hold_ms=100,after_ms=300)
 assert s.halted is None and not report['guest_writers'] and not report['host_queue_writes'] and not report['bulk_overlaps'] and not report['copier_or_reset_entries'] and bytes(u.mem_read(LO,spec['storage_bytes']))==initial
 assert not any(v['overlaps_queue'] for v in report['DMA'].values())
 report.update(passed=True,elapsed_model_ms=s.now_ms(),bulk_calls=dict(report['bulk_calls']),halted=s.halted,MIDI_received=mi.received,MIDI_delivered=mi.delivered,pattern_backing_before=hex(before),pattern_backing_after=hex(after),pattern_replacement_confirmed=before!=after,queue_unchanged=True,pcm_bytes=len(s.pcm))
except Exception:report.update(passed=False,failure=traceback.format_exc());print(report['failure'],flush=True)
finally:
 if s:s.close()
report['limits']=['Guest and host API writes observed in one finite restored session; native DMA/device writes outside these model APIs remain unproved.','Descriptor envelopes include partial guest programming states conservatively; unknown flags and scatter-gather successors remain explicit, not certified absent.','Clock/cache costs and emulated peripherals do not prove physical DMA configuration or timing.','Pattern request is confirmed as a replacement only if the backing actually changes.']
Path('outputs/Digitone-E04-PC-resident-storage-extended-runtime.json').write_text(json.dumps(report,indent=2));print('RUNTIME',report['passed'],len(report['DMA']),flush=True)
if not report['passed']:raise SystemExit(1)
