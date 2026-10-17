"""Cycle-clock render and DMA measurements, ephemeral PC overlays only."""
import pathlib,json,struct,collections,traceback,time
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('def run(mode):')[0])
from emu.cftiming import deadline_report,measured_period
import emu.cftiming as timing
class RoundRobinCache:
 def __init__(self):
  self.tags=[[None]*4 for _ in range(128)];self.next=[0]*128;self.hits=self.misses=0
 def touch(self,addr,size):
  if not 0x40000000<=addr<0x48000000:return 0
  misses=0
  for line in range(addr//16,(addr+size-1)//16+1):
   index=line%128;row=self.tags[index]
   if line in row:self.hits+=1
   else:
    slot=row.index(None) if None in row else self.next[index]
    row[slot]=line;self.next[index]=(slot+1)%4;self.misses+=1;misses+=1
  return misses
timing.ICache=RoundRobinCache
PENALTY=int(os.environ.get('DEADLINE_MISS_PENALTY','20'))
FSYS=int(os.environ.get('DEADLINE_FSYS','250000000'))
OUT=pathlib.Path(os.environ.get('DEADLINE_OUT','outputs/Digitone-cycle-audio-deadlines.json'))
report={'fsys_assumption_hz':FSYS,'firmware_modified':False,'firmware_before':hashlib.sha256(SYX.read_bytes()).hexdigest(),'runs':[],'failure':None,'model':{'clock':'CycleClock: instruction timing tables, stalls, max branch ranges','memory':'Instruction-cache round-robin sensitivity only; no data-cache timing, DDR contention or store-buffer timing','hle':False,'DMA':'Existing SSI bulk-capture model; not physical sample-by-sample bus timing'}}
specs=[(0x40093ef4,'producer_capture','4ef9',8),(0x400f0626,'allocate_clear','4ef9',6),(0x4009dda6,'before','4eb9',6),(0x4009de46,'caller_commit','4ef9',10),(0x4009df9a,'pitch_hook','4ef9',8)]
began=time.monotonic()
def persist():report['elapsed_seconds']=round(time.monotonic()-began,1);OUT.write_text(json.dumps(report,indent=2))
def run(mode):
 rec={'mode':mode,'DMA_captures':[],'render_windows':[],'hooks':{},'pitch':[],'quantizer_calls':[],'candidate_fixture':[]};report['runs'].append(rec)
 last_store={};last_capture={};waiting=collections.defaultdict(list);counts=collections.Counter();writes=0
 def install(session):
  m=session.m;uc=m.uc;m.ensure(RAM);rec['initial_control_registers']={hex(k):hex(v) for k,v in m.ctlregs.items()}
  if mode!='stock':
   uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1));m.install_isa_patches_scoped(blob,RAM)
   if mode=='all':
    for pc,name,op,n in specs:
     assert bytes(uc.mem_read(pc,n))==stock[pc-base:pc-base+n]
     uc.mem_write(pc,bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((n-6)//2))
   elif mode=='sham':
    addr=RAM+0xe00;uc.mem_write(addr,stock[0x4009df9a-base:0x4009dfa2-base]+bytes.fromhex('4ef9')+u32(0x4009dfa2));uc.mem_write(0x4009df9a,bytes.fromhex('4ef9')+u32(addr)+bytes.fromhex('4e71'))
  def stamp():return {'cycles':session.clock.cycles,'timer_cycles':session.pits.now-session._t0,'ms':session.now_ms()}
  for label,pc in [('allocator',0x400f0626),('producer',0x40093ef4),('acceptance',0x4009dd80),('pitch',0x4009df9a)]:session.at(pc,lambda uc,a,n,d,label=label:counts.update([label]))
  def pitch(uc,pc,n,d):
   event=uc.reg_read(UC_M68K_REG_A3);rec['pitch'].append(dict(stamp(),track=rd(uc,event+8),fixed_note=uc.reg_read(UC_M68K_REG_D6)))
  session.at(0x4009dfa8,pitch)
  if mode=='all':
   def quantize(uc,pc,n,d):
    sp=uc.reg_read(UC_M68K_REG_A7);note=rd(uc,sp+4);word=rd(uc,sp+8);rec['quantizer_calls'].append(dict(stamp(),note=note,word=hex(word),expected=oracle(note,word)))
   session.at(layout['quantize']['address'],quantize)
   if os.environ.get('DEADLINE_SCALE')=='1':
    def source_scale(uc,pc,n,d):
     track=uc.reg_read(UC_M68K_REG_D4);back=uc.reg_read(UC_M68K_REG_A3)
     if track==2:uc.mem_write(back+track*0x3d0+0x3cb,b'\x3d');uc.mem_write(back+track*0x3d0+0x3ce,b'\0')
    session.at(0x40093ef4,source_scale)
   if os.environ.get('DEADLINE_VALID_CONTEXT')=='1':
    # Explicit diagnostic fixture for the unimplemented cached-producer copy.
    # Stock acceptance and native retained commit/read/quantizer still execute.
    def candidate_fixture(uc,pc,n,d):
     event=uc.reg_read(UC_M68K_REG_A3);track=rd(uc,event+8);offset=event-0x4199da94
     if track==2 and 0<=offset<128*72 and offset%72==0:
      word=0x800040bd;uc.mem_write(BSS+32+offset//72*4,u32(word));rec['candidate_fixture'].append(dict(stamp(),event=hex(event),word=hex(word)))
    session.at(0x4009de46,candidate_fixture)
  ssi=session.ev['ssi0_dma'];sink=ssi.sink
  def store(uc,access,addr,n,value,d):
   nonlocal writes
   writes+=1;now=session.clock.cycles
   for word in range(addr,addr+n,4):
    last_store[word]=now
    for index in waiting.pop(word,[]):
     item=rec['DMA_captures'][index];item['next_completion_cycles']=now;item['completion_margin_cycles']=item['cycles']-now;item['completion_margin_us']=(item['cycles']-now)*1e6/FSYS
  uc.hook_add(UC_HOOK_MEM_WRITE,store,begin=0x80001000,end=0x80002fff)
  def captured(raw):
   descriptor=bytes(uc.mem_read(ssi._tcd(ssi.p.tx_chan),32));end=struct.unpack('>I',descriptor[:4])[0];start=end-len(raw);final=end-4
   item=dict(stamp(),start=hex(start),end=hex(end),bytes=len(raw),pc=hex(uc.reg_read(UC_M68K_REG_PC)),a0=hex(uc.reg_read(UC_M68K_REG_A0)),d4=uc.reg_read(UC_M68K_REG_D4),last_word_store_cycles=last_store.get(final),previous_capture_cycles=last_capture.get(final))
   fresh=final in last_store and (final not in last_capture or last_store[final]>last_capture[final])
   prior=last_capture.get(final,-1);words=list(range(start,end,4));observed=[last_store.get(w) for w in words]
   item['all_words_observed']=all(t is not None for t in observed)
   item['unfresh_words']=sum(t is None or t<=prior for t in observed)
   item['fresh_final_store_observed']=fresh
   if fresh:
    item['completion_margin_cycles']=item['cycles']-last_store[final];item['completion_margin_us']=item['completion_margin_cycles']*1e6/FSYS
   else:waiting[final].append(len(rec['DMA_captures']))
   item['capture_inside_pending_mixer_store']=0x40096bf6<=int(item['pc'],16)<=0x40096c30 and start<=int(item['a0'],16)<end
   last_capture[final]=item['cycles'];rec['DMA_captures'].append(item);sink(raw)
  ssi.sink=captured
  for name in ['_render_started','_render_returned']:
   original=getattr(ssi,name)
   def window(*args,name=name,original=original):
    rec['render_windows'].append(dict(stamp(),event=name,pc=hex(uc.reg_read(UC_M68K_REG_PC))))
    return original(*args)
   setattr(ssi,name,window)
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,hle=False,timing={'fsys':FSYS,'accel':'max','stalls':True,'icache':True,'miss_penalty':PENALTY},on_machine=install)
 try:
  session.run_ms(20)
  if os.environ.get('DEADLINE_PATTERN'):
   session.press(session.code('PTN'));session.run_ms(20);session.tap(session.code(os.environ['DEADLINE_PATTERN']),hold_ms=20,after_ms=20);session.release(session.code('PTN'));session.run_ms(40)
  session.tap(session.code('PLAY'),hold_ms=20,after_ms=int(os.environ.get('DEADLINE_PLAY_MS','60')));session.tap(session.code('STOP'),hold_ms=20,after_ms=20)
  rec.update(clock=session.clock.report(),halted=session.halted,ms=session.ms,hooks=dict(counts),audio_bytes=len(session.pcm),audio_sha256=hashlib.sha256(session.pcm).hexdigest(),watched_SRAM_writes=writes)
  rec['render_deadline']=deadline_report(session.clock,191,round(FSYS*32/48000));rec['measured_render_period_cycles']=measured_period(session.clock,191)
  captures=[x for x in rec['DMA_captures'] if x['ms']>=20];resolved=[x for x in captures if 'completion_margin_cycles' in x];margins=[x['completion_margin_us'] for x in resolved]
  rec['DMA_summary']={'after_warmup_captures':len(captures),'resolved':len(resolved),'unresolved':len(captures)-len(resolved),'late':sum(x['completion_margin_cycles']<0 for x in resolved),'minimum_margin_us':min(margins) if margins else None,'maximum_margin_us':max(margins) if margins else None,'pending_mixer_capture_count':sum(x['capture_inside_pending_mixer_store'] for x in captures),'captures_with_unfresh_words':sum(x.get('unfresh_words',0)>0 for x in captures),'maximum_clock_timer_gap_cycles':max((x['cycles']-x['timer_cycles'] for x in captures),default=0)}
  rec['decoder_flags']=[{'flags':k[0],'address':hex(k[1]),'op':k[2],'blocks':v} for k,v in session.clock.flagged.items()]
  assert session.halted is None
  print(mode,'ms',rec['ms'],'mismatches',rec['clock']['decode_mismatches'],'render',rec['render_deadline'],'DMA',rec['DMA_summary'],flush=True)
 finally:session.close();persist()
try:
 for mode in os.environ.get('DEADLINE_RUNS','stock,sham,all').split(','):run(mode)
 report['firmware_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();assert report['firmware_before']==report['firmware_after']
except BaseException as exc:report['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(report['failure']['traceback'],flush=True)
finally:persist()
