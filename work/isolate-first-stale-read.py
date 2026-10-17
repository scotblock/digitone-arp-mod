"""Cycle-clock render and DMA measurements, ephemeral PC overlays only."""
import pathlib,json,struct,collections,traceback,time
p=pathlib.Path('work/test-native-arp-overlays.py').read_text().split('\ndef run(mode):')[0]
p='\n'.join(line for line in p.splitlines() if not line.startswith('subprocess.run('))
exec(p)
from emu.cftiming import deadline_report,measured_period
from emu import edma_sw
from phase_audio_dma import PhaseAudioMemory as MemoryTiming
original_bank=edma_sw.install_bank
def python_bank(m,ev,**kw):
 kw['native']=False
 return original_bank(m,ev,**kw)
edma_sw.install_bank=python_bank
FSYS=int(os.environ.get('DEADLINE_FSYS','250000000'))
OUT=pathlib.Path(os.environ.get('DEADLINE_OUT','outputs/Digitone-cycle-audio-deadlines.json'))
report={'experiment':'first stale read controls, exact 0-80 ms workload prefix','clock_candidates_hz':[250000000,264000000],'fsys_assumption_hz':FSYS,'firmware_modified':False,'firmware_before':hashlib.sha256(SYX.read_bytes()).hexdigest(),'runs':[],'failure':None,'model':{'clock':'CycleClock: instruction timing tables, stalls, max branch ranges','memory':'Cache maintenance and serialized DDR resource sensitivity; timestamped DMA payload beats and completion; no physical cache-value simulation','hle':False,'DMA':'Frame-level SSI capture; software DMA payload at modeled beat boundaries'}}
specs=[(0x40093ef4,'producer_capture','4ef9',8),(0x400f0626,'allocate_clear','4ef9',6),(0x4009dda6,'before','4eb9',6),(0x4009de46,'caller_commit','4ef9',10),(0x4009df9a,'pitch_hook','4ef9',8)]
began=time.monotonic()
def persist():report['elapsed_seconds']=round(time.monotonic()-began,1);OUT.write_text(json.dumps(report,indent=2))
def run(mode):
 rec={'mode':mode,'DMA_captures':[],'render_windows':[],'hooks':{},'pitch':[],'quantizer_calls':[],'candidate_fixture':[]};report['runs'].append(rec)
 last_store={};last_capture={};waiting=collections.defaultdict(list);counts=collections.Counter();writes=0
 def install(session):
  m=session.m;uc=m.uc;m.ensure(RAM);session.memtime=MemoryTiming(session,fill=int(os.environ.get('MEM_FILL','20')),writeback=int(os.environ.get('MEM_WRITEBACK','16')),beat=int(os.environ.get('MEM_BEAT','4')),contention=os.environ.get('MEM_CONTENTION','1')=='1')
  if mode in ('all','all_fixed','context_only','sham'):
   uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1));m.install_isa_patches_scoped(blob,RAM)
   if mode in ('all','all_fixed','context_only'):
    for pc,name,op,n in specs:
     if mode=='context_only' and name=='pitch_hook':continue
     assert bytes(uc.mem_read(pc,n))==stock[pc-base:pc-base+n]
     uc.mem_write(pc,bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((n-6)//2))
   elif mode=='sham':
    addr=RAM+0xe00;uc.mem_write(addr,stock[0x4009df9a-base:0x4009dfa2-base]+bytes.fromhex('4ef9')+u32(0x4009dfa2));uc.mem_write(0x4009df9a,bytes.fromhex('4ef9')+u32(addr)+bytes.fromhex('4e71'))
  rec['clock_source']={'source':'SSI_CLKIN selected by stock MISCCR clear','external_hz_candidate':12288000,'frame_hz_conditional':48000,'core_hz_candidate':FSYS,'bus_hz_candidate':FSYS//2}
  rec['CCM_at_snapshot']={hex(a):bytes(uc.mem_read(a,2)).hex() for a in (0xec09000e,0xec090010)}
  rec['SSI_runtime_writes']=[]
  def ssi_write(uc,access,addr,n,value,data):
   rec['SSI_runtime_writes'].append(dict(stamp(),address=hex(addr),size=n,value=hex(value)))
  uc.hook_add(UC_HOOK_MEM_WRITE,ssi_write,begin=0xfc0c8010,end=0xfc0c802f)
  def stamp():return {'cycles':session.clock.cycles,'timer_cycles':session.pits.now-session._t0,'ms':session.now_ms()}
  for label,pc in [('allocator',0x400f0626),('producer',0x40093ef4),('acceptance',0x4009dd80),('pitch',0x4009df9a)]:session.at(pc,lambda uc,a,n,d,label=label:counts.update([label]))
  rec['cost_ablation']={'helper_memory_neutral':os.environ.get('NEUTRAL_HELPER_MEMORY')=='1','helper_compute_neutral':os.environ.get('NEUTRAL_HELPER_COMPUTE')=='1','removed_memory_cycles':0,'removed_compute_cycles':0}
  rec['block_costs']=[];rec['queue_trace']=[]
  mem=session.memtime;c=session.clock
  def helper(a):return RAM<=a<RAM+len(blob)
  if rec['cost_ablation']['helper_memory_neutral']:
   for name in ('fetch','data'):
    original=getattr(mem,name)
    def neutral(*args,name=name,original=original):
     address=args[0];active=helper(address) if name=='fetch' else helper(uc.reg_read(UC_M68K_REG_PC))
     if not active:return original(*args)
     old_cycles,old_left,old_free=c.cycles,c.left,mem.bus.free
     answer=original(*args);rec['cost_ablation']['removed_memory_cycles']+=c.cycles-old_cycles
     c.cycles,c.left,mem.bus.free=old_cycles,old_left,old_free
     return answer
    setattr(mem,name,neutral)
  original_block=c._on_block
  uc.hook_del(c.hook)
  def traced_block(uc,addr,size,data):
   before=c.cycles;memory_before=sum(v for k,v in mem.counts.items() if k.endswith('_stall_cycles'));flow_before=c.flow_cycles;instructions_before=c.instructions
   original_block(uc,addr,size,data)
   cost=c.cycles-before;memory=sum(v for k,v in mem.counts.items() if k.endswith('_stall_cycles'))-memory_before
   # Memory-neutral fetch counters retain the hypothetical original charge.
   if (rec['cost_ablation']['helper_memory_neutral'] or (rec.get('pitch_fetch_ablation',{}).get('enabled') and rec['pitch_fetch_ablation']['active'])) and helper(addr):memory=0
   compute=cost-memory
   if rec['cost_ablation']['helper_compute_neutral'] and helper(addr) and compute>0:
    c.cycles-=compute
    if c.left is not None:c.left+=compute
    rec['cost_ablation']['removed_compute_cycles']+=compute
   if 55<=session.now_ms()<=64 and len(rec['block_costs'])<120000:
    rec['block_costs'].append({'cycles':before,'pc':hex(addr),'size':size,'helper':helper(addr),'charged_cycles':c.cycles-before,'compute_cycles_before_ablation':compute,'fetch_stall_cycles_before_ablation':memory,'flow_cycles':c.flow_cycles-flow_before,'instructions':c.instructions-instructions_before,'active_vectors':[x[0] for x in c._frames]})
  c.hook=uc.hook_add(UC_HOOK_BLOCK,traced_block)
  def queue_trace(uc,pc,n,d):
   if 45<=session.now_ms()<=75:
    sp=uc.reg_read(UC_M68K_REG_A7);event=rd(uc,sp+4)
    rec['queue_trace'].append(dict(stamp(),pc=hex(pc),event=hex(event),kind=rd(uc,event),track=rd(uc,event+8),timestamp=rd(uc,sp+8),queue_clock=rd(uc,0x413360e8)))
  session.at(0x400f07ac,queue_trace)
  rec['transport_trace']=[]
  def transport_write(uc,access,address,n,value,d):
   rec['transport_trace'].append(dict(stamp(),pc=hex(uc.reg_read(UC_M68K_REG_PC)),address=hex(address),size=n,value=hex(value),queue_clock=rd(uc,0x413360e8)))
  uc.hook_add(UC_HOOK_MEM_WRITE,transport_write,begin=profile.transport_state,end=profile.transport_state+3)
  if profile.transport_start:session.at(profile.transport_start,lambda uc,pc,n,d:rec['transport_trace'].append(dict(stamp(),label='transport_start_entry',pc=hex(pc),queue_clock=rd(uc,0x413360e8))))
  rec['pitch_fetch_ablation']={'enabled':os.environ.get('NEUTRAL_PITCH_FETCH')=='1','active':False,'removed_fetch_cycles':0}
  if rec['pitch_fetch_ablation']['enabled']:
   old_fetch=mem.fetch
   def neutral_pitch_fetch(address,size):
    if not (rec['pitch_fetch_ablation']['active'] and helper(address)):return old_fetch(address,size)
    before,left,free=c.cycles,c.left,mem.bus.free
    answer=old_fetch(address,size);rec['pitch_fetch_ablation']['removed_fetch_cycles']+=c.cycles-before
    c.cycles,c.left,mem.bus.free=before,left,free
    return answer
   mem.fetch=neutral_pitch_fetch
  rec['diagnostic_pitch_controls']=[];original_notes={}
  def original_note(uc,pc,n,d):
   rec['pitch_fetch_ablation']['active']=True
   event=uc.reg_read(UC_M68K_REG_A3);original_notes[event]=uc.reg_read(UC_M68K_REG_D6)&65535
  session.at(0x4009df9a,original_note)
  def control_pitch(uc,pc,n,d):
   event=uc.reg_read(UC_M68K_REG_A3);before=uc.reg_read(UC_M68K_REG_D6);original=original_notes[event]<<16;track=rd(uc,event+8)
   if mode=='all_fixed':uc.reg_write(UC_M68K_REG_D6,original)
   elif mode=='stock_changed' and track==2:uc.reg_write(UC_M68K_REG_D6,oracle(original>>16,0x800040bd)<<16)
   if mode in ('stock','sham'):assert before==original
   rec['diagnostic_pitch_controls'].append(dict(stamp(),event=hex(event),track=track,original_fixed=original,computed_fixed=before,delivered_fixed=uc.reg_read(UC_M68K_REG_D6)))
  session.at(0x4009dfa8,control_pitch)
  rec['checkpoints']=[]
  def checkpoint(uc,pc,n,d,label):
   ms=session.now_ms()
   if 45<=ms<=75:
    rec['checkpoints'].append(dict(stamp(),label=label,pc=hex(pc),instructions=session.clock.instructions,stall_cycles=session.clock.stall_cycles,flow_cycles=session.clock.flow_cycles,memory_counts=dict(session.memtime.counts),bus_counts=dict(session.memtime.bus.counts),bus_free=session.memtime.bus.free,vector_counts={str(k):v.count for k,v in session.clock.vectors.items()}))
  for name,r in layout.items():
   session.at(r['address'],lambda uc,pc,n,d,name=name:checkpoint(uc,pc,n,d,'helper_'+name))
  for pc,label in [(0x4009dd80,'acceptance'),(0x4009dda6,'before_call'),(0x4009de46,'commit'),(0x4009df9a,'pitch_entry'),(0x4009dfa8,'pitch_output'),(0x4009e720,'dispatch'),(0x4009c838,'render_entry'),(0x4009ba70,'renderer_return')]:
   session.at(pc,lambda uc,pc,n,d,label=label:checkpoint(uc,pc,n,d,label))
  def pitch(uc,pc,n,d):
   event=uc.reg_read(UC_M68K_REG_A3);rec['pitch'].append(dict(stamp(),track=rd(uc,event+8),fixed_note=uc.reg_read(UC_M68K_REG_D6)))
  session.at(0x4009dfa8,pitch)
  if mode in ('all','all_fixed','context_only'):
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
     if (track<4 if os.environ.get('STRESS_CAPTURE_ALL')=='1' else track==2) and 0<=offset<128*72 and offset%72==0:
      word=(0x800000bd|(track<<13));uc.mem_write(BSS+32+offset//72*4,u32(word));rec['candidate_fixture'].append(dict(stamp(),event=hex(event),word=hex(word)))
    session.at(0x4009de46,candidate_fixture)
  ssi=session.ev['ssi0_dma'];ssi.batch=False;sink=ssi.sink
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
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,hle=False,timing={'fsys':FSYS,'accel':'max','stalls':True,'icache':True},on_machine=install)
 try:
  rec['workload']=[]
  def mark(name):rec['workload'].append(dict(name=name,ms=session.now_ms(),cycles=session.clock.cycles,producer_count=counts['producer'],pitch_count=counts['pitch'],backing=hex(rd(session.m.uc,0x41342150))))
  def pattern(n):
   session.press(session.code('PTN'));session.run_ms(5)
   session.tap(session.code(str(n)),hold_ms=5,after_ms=5)
   session.release(session.code('PTN'));session.run_ms(15)
   mark('requested pattern '+str(n))
  session.run_ms(10)
  if os.environ.get('STRESS_PATTERN_TWO')=='1':pattern(2)
  session.tap(session.code('PLAY'),hold_ms=10,after_ms=30)
  mark('prefix ends at 80 ms before keyboard input')
  rec.update(memory_model=session.memtime.report(),clock=session.clock.report(),halted=session.halted,ms=session.ms,hooks=dict(counts),audio_bytes=len(session.pcm),audio_sha256=hashlib.sha256(session.pcm).hexdigest(),watched_SRAM_writes=writes)
  rec['render_deadline']=deadline_report(session.clock,191,round(FSYS*32/48000));rec['measured_render_period_cycles']=measured_period(session.clock,191)
  captures=[x for x in rec['DMA_captures'] if x['ms']>=20];resolved=[x for x in captures if 'completion_margin_cycles' in x];margins=[x['completion_margin_us'] for x in resolved]
  rec['DMA_summary']={'after_warmup_captures':len(captures),'resolved':len(resolved),'unresolved':len(captures)-len(resolved),'late':sum(x['completion_margin_cycles']<0 for x in resolved),'minimum_margin_us':min(margins) if margins else None,'maximum_margin_us':max(margins) if margins else None,'pending_mixer_capture_count':sum(x['capture_inside_pending_mixer_store'] for x in captures),'captures_with_unfresh_words':sum(x.get('unfresh_words',0)>0 for x in captures),'final_clock_timer_gap_cycles':session.clock.cycles-(session.pits.now-session._t0),'maximum_clock_timer_gap_cycles':max((x['cycles']-x['timer_cycles'] for x in captures),default=0)}
  rec['decoder_flags']=[{'flags':k[0],'address':hex(k[1]),'op':k[2],'blocks':v} for k,v in session.clock.flagged.items()]
  assert session.halted is None
  print(mode,'ms',rec['ms'],'mismatches',rec['clock']['decode_mismatches'],'render',rec['render_deadline'],'DMA',rec['DMA_summary'],flush=True)
 finally:session.close();persist()
try:
 FSYS=264000000
 run(os.environ.get('STRESS_MODE','stock'))
 report['runs'][-1]['fsys_assumption_hz']=FSYS
 report['firmware_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();assert report['firmware_before']==report['firmware_after']
except BaseException as exc:report['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(report['failure']['traceback'],flush=True)
finally:persist()
