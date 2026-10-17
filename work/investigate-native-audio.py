"""Paired deterministic audio probes and hook ablations, no file firmware patch."""
import pathlib,json,hashlib,struct,traceback,collections
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('def run(mode):')[0])
import numpy as np
OUT=pathlib.Path(os.environ.get('AUDIO_PROBE_OUT','outputs/Digitone-native-audio-investigation.json'))
report={'firmware_modified':False,'firmware_before':hashlib.sha256(SYX.read_bytes()).hexdigest(),'runs':[],'comparisons':[],'failure':None,'snapshot':str(paths.gui)}
specs=[(0x40093ef4,'producer_capture','4ef9',8),(0x400f0626,'allocate_clear','4ef9',6),(0x4009dda6,'before','4eb9',6),(0x4009de46,'caller_commit','4ef9',10),(0x4009df9a,'pitch_hook','4ef9',8)]
def persist():OUT.write_text(json.dumps(report,indent=2))
def run(mode):
 rec={'mode':mode,'pitch':[],'dispatch':[],'dsp':[],'hits':{},'inputs':[],'ssi_chunks':[],'render_windows':[]};report['runs'].append(rec);hits=collections.Counter();packets=[];voices=[]
 def install(session):
  if mode.startswith('exact-'):session.stepper=False
  uc=session.m.uc;session.m.ensure(RAM)
  if mode not in ['stock','stock-repeat','exact-stock']:
   uc.mem_write(RAM,blob);uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1));session.m.install_isa_patches_scoped(blob,RAM)
   for pc,name,op,n in specs:
    enabled=mode=='all' or mode in ['pitch-only','exact-pitch'] and name=='pitch_hook' or mode=='allocator-only' and name=='allocate_clear'
    if enabled:
     assert bytes(uc.mem_read(pc,n))==stock[pc-base:pc-base+n]
     uc.mem_write(pc,bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((n-6)//2))
   if mode in ['sham','exact-sham']:
    address=RAM+0xe00;code=stock[0x4009df9a-base:0x4009dfa2-base]+bytes.fromhex('4ef9')+u32(0x4009dfa2)
    uc.mem_write(address,code);uc.mem_write(0x4009df9a,bytes.fromhex('4ef9')+u32(address)+bytes.fromhex('4e71'))
  def timed():return {'ms':session.now_ms(),'pcm_frames_collected':len(session.pcm)//4}
  def pitch(uc,pc,n,d):
   event=uc.reg_read(UC_M68K_REG_A3);rec['pitch'].append(dict(timed(),track=rd(uc,event+8),note=uc.reg_read(UC_M68K_REG_D6),event=hex(event),type=rd(uc,event),flags=hex(rd(uc,event+40))))
  def dispatch(uc,pc,n,d):
   sp=uc.reg_read(UC_M68K_REG_A7);args=list(struct.unpack('>9I',uc.mem_read(sp+4,36)));rec['dispatch'].append(dict(timed(),args=args))
  session.at(0x4009dfa8,pitch);session.at(0x4009e720,dispatch)
  for label,pc in [('allocator',0x400f0626),('producer',0x40093ef4),('acceptance',0x4009dd80),('pitch',0x4009df9a)]:session.at(pc,lambda uc,a,n,d,label=label:hits.update([label]))
  link=session.ev.get('dsplink')
  if link is None:
   link=next((v for v in session.ev.values() if hasattr(v,'_service_dsp')),None)
  assert link is not None and not link.threaded
  original=link._service_dsp
  def service(d,elapsed,taken=False):
   before=link.renders;packet=bytes(link._buf.raw[:0x3a0]);stamp=timed();answer=original(d,elapsed,taken=taken)
   if link.renders>before:
    packets.append(packet);rec['dsp'].append(dict(stamp,render=link.renders,sha256=hashlib.sha256(packet).hexdigest()))
   return answer
  link._service_dsp=service
  if os.environ.get('AUDIO_DEEP')=='1':
   # Keep a second wrapper so the original first-pass traces remain unchanged.
   wrapped=link._service_dsp
   def with_voices(d,elapsed,taken=False):
    before=link.renders;answer=wrapped(d,elapsed,taken=taken)
    if link.renders>before:
     voice=bytes(link._buf.raw[0x3a0:0x7a0]);voices.append(voice);rec['dsp'][-1]['voice_sha256']=hashlib.sha256(voice).hexdigest()
    return answer
   link._service_dsp=with_voices
   ssi=session.ev['ssi0_dma'];sink=ssi.sink
   def captured(raw):
    descriptor=bytes(uc.mem_read(ssi._tcd(ssi.p.tx_chan),32))
    rec['ssi_chunks'].append(dict(timed(),ssi_now=ssi.now,pc=hex(uc.reg_read(UC_M68K_REG_PC)),a0=hex(uc.reg_read(UC_M68K_REG_A0)),d4=uc.reg_read(UC_M68K_REG_D4),SR=hex(uc.reg_read(UC_M68K_REG_SR)),tx_descriptor=descriptor.hex(),raw_tail=bytes(raw[-64:]).hex(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    sink(raw)
   ssi.sink=captured
   for name in ['_render_started','_render_returned']:
    original_window=getattr(ssi,name)
    def window(*args,name=name,original_window=original_window):
     rec['render_windows'].append(dict(timed(),event=name,ssi_now=ssi.now,pc=hex(uc.reg_read(UC_M68K_REG_PC))))
     return original_window(*args)
    setattr(ssi,name,window)
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=install)
 try:
  session.tap(session.code('PLAY'),hold_ms=50,after_ms=int(os.environ.get('AUDIO_PLAY_MS','1500')));session.tap(session.code('STOP'),hold_ms=50,after_ms=200)
  rec.update(hits=dict(hits),inputs=session.inputs,ms=session.ms,halted=session.halted,audio_bytes=len(session.pcm),audio_sha256=hashlib.sha256(session.pcm).hexdigest())
  assert session.halted is None
  pathlib.Path('work/'+OUT.stem+'-'+mode+'.pcm').write_bytes(session.pcm)
  pathlib.Path('work/'+OUT.stem+'-'+mode+'-packets.bin').write_bytes(b''.join(packets))
  if voices:pathlib.Path('work/'+OUT.stem+'-'+mode+'-voices.bin').write_bytes(b''.join(voices))
 finally:session.close();persist()
 print(mode,rec['hits'],'pitch',len(rec['pitch']),'renders',len(rec['dsp']),rec.get('audio_sha256'),flush=True)
def compare(a,b):
 x=report['runs'][a];y=report['runs'][b];left=np.frombuffer(pathlib.Path('work/'+OUT.stem+'-'+x['mode']+'.pcm').read_bytes(),dtype='<i2').reshape(-1,2);right=np.frombuffer(pathlib.Path('work/'+OUT.stem+'-'+y['mode']+'.pcm').read_bytes(),dtype='<i2').reshape(-1,2);n=min(len(left),len(right));bad=np.flatnonzero(np.any(left[:n]!=right[:n],axis=1));noteequal=[(p['track'],p['note'],p['type'],p['flags']) for p in x['pitch']]==[(p['track'],p['note'],p['type'],p['flags']) for p in y['pitch']]
 dispatch_equal=[d['args'] for d in x['dispatch']]==[d['args'] for d in y['dispatch']]
 hashesx=[d['sha256'] for d in x['dsp']];hashesy=[d['sha256'] for d in y['dsp']];packetbad=next((i for i,(a,b) in enumerate(zip(hashesx,hashesy)) if a!=b),None)
 c={'left':x['mode'],'right':y['mode'],'inputs_equal':x['inputs']==y['inputs'],'audio_equal':len(left)==len(right) and not len(bad),'frames_left':len(left),'frames_right':len(right),'differing_frames':len(bad),'first_audio_difference_frame':int(bad[0]) if len(bad) else None,'first_audio_difference_ms':float(bad[0]/48) if len(bad) else None,'pitch_values_equal':noteequal,'dispatch_args_equal':dispatch_equal,'dsp_packet_sequences_equal':hashesx==hashesy,'first_dsp_packet_difference':packetbad,'pitch_time_deltas_ms':[j['ms']-i['ms'] for i,j in zip(x['pitch'],y['pitch'])],'dispatch_time_deltas_ms':[j['ms']-i['ms'] for i,j in zip(x['dispatch'],y['dispatch'])]}
 if len(bad):
  k=int(bad[0]);c['first_audio_left']=left[k].tolist();c['first_audio_right']=right[k].tolist()
 if packetbad is not None:
  c['first_dsp_left']=x['dsp'][packetbad];c['first_dsp_right']=y['dsp'][packetbad]
  rawx=pathlib.Path('work/'+OUT.stem+'-'+x['mode']+'-packets.bin').read_bytes()[packetbad*0x3a0:(packetbad+1)*0x3a0];rawy=pathlib.Path('work/'+OUT.stem+'-'+y['mode']+'-packets.bin').read_bytes()[packetbad*0x3a0:(packetbad+1)*0x3a0];c['first_dsp_changed_bytes']=[{'offset':hex(i),'left':a,'right':b} for i,(a,b) in enumerate(zip(rawx,rawy)) if a!=b]
 if os.environ.get('AUDIO_DEEP')=='1':
  c['dsp_voice_sequences_equal']=[d.get('voice_sha256') for d in x['dsp']]==[d.get('voice_sha256') for d in y['dsp']]
  c['first_ssi_chunk_difference']=next((i for i,(a,b) in enumerate(zip(x['ssi_chunks'],y['ssi_chunks'])) if a['sha256']!=b['sha256']),None)
  c['render_windows_equal']=x['render_windows']==y['render_windows']
  c['first_render_window_difference']=next((i for i,(a,b) in enumerate(zip(x['render_windows'],y['render_windows'])) if a!=b),None)
 report['comparisons'].append(c);persist();print('COMPARE',x['mode'],y['mode'],'audio',c['audio_equal'],'first',c['first_audio_difference_ms'],'packet',packetbad,flush=True)
try:
 for mode in os.environ.get('AUDIO_PROBE_RUNS','stock,stock-repeat,all,pitch-only,allocator-only').split(','):run(mode)
 for i in range(1,len(report['runs'])):compare(0,i)
 report['firmware_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();assert report['firmware_before']==report['firmware_after']
except BaseException as exc:report['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(report['failure']['traceback'],flush=True)
finally:persist()
