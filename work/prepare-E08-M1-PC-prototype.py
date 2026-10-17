from pathlib import Path
p=Path('work/trace-E08-MIDI-track-queue.py').read_text()
p=p.replace("'firmware_unchanged':True", "'firmware_unchanged':True,'prototype_kind':'Host-assisted PC scheduler feeding native guest MIDI task; not a machine-code patch'")
p=p.replace("'queue_samples':[]}","'queue_samples':[],'phases':[],'captures':[],'generations':[],'cancellations':[],'clock_samples':[]}")
a=p.index(' def queue(u,pc,n,d):');z=p.index(' mo=midi.MidiOut(',a)
p=p[:a]+''' s.m.ensure(ARENA)
 def stamp():return rd(s.m.uc,0x80004614)
 def due(now,then):return ((now-then)&0xffffffff)<0x80000000
 def emit(u,original,now):
  st=state['active'];assert st['interval']>0 and st['gate']>0;blob=bytearray(st['template']);note=st['notes'][st['index']%len(st['notes'])];st['index']+=1;st['next']=(st['next']+st['interval'])&0xffffffff
  struct.pack_into('>I',blob,0x10,1);blob[0x14:0x1c]=bytes(8);blob[0x14]=note
  struct.pack_into('>I',blob,0x1c,st['gate']);struct.pack_into('>I',blob,0x24,now);struct.pack_into('>I',blob,0x28,0);struct.pack_into('>I',blob,0x30,original)
  u.mem_write(ARENA,bytes(blob));u.reg_write(UC_M68K_REG_A2,ARENA)
  out['generations'].append({'phase':state['phase'],'ms':s.now_ms(),'note':note,'source_index':st['index']-1,'native_timestamp':now,'native_gate':st['gate']})
 def queue(u,pc,n,d):
  a=u.reg_read(UC_M68K_REG_A2)
  if a==ARENA:return
  v=[rd(u,a+i*4) for i in range(13)];kind=v[0];k=str(kind);out['queue_counts'][k]=out['queue_counts'].get(k,0)+1
  if out['queue_counts'][k]<=12:out['queue_samples'].append({'ms':s.now_ms(),'pointer':hex(a),'words':[hex(x) for x in v]})
  now=stamp()
  if state['active'] and state['phase'].startswith('UP'):
   if kind==4 or (s.profile.transport_state and rd(u,s.profile.transport_state)!=1):
    out['cancellations'].append({'phase':state['phase'],'reason':'native_stop_dispatch' if kind==4 else 'native_transport_stopped','ms':s.now_ms()});state['active']=None
   elif due(now,state['active']['expiry']):
    out['cancellations'].append({'phase':state['phase'],'reason':'source_gate_expired','ms':s.now_ms()});state['active']=None
  if kind in [0,1] and v[1]==0 and v[2]==1 and v[4]>=3:
   raw=bytes(u.mem_read(a,52));notes=list(raw[0x14:0x14+v[4]]);basegate=v[7];assert basegate>0
   # Disclosed equal source-gate fixture: eight times the native default length,
   # preserving a guest-produced three-note chord, channel and velocity.
   u.mem_write(a+0x1c,struct.pack('>I',basegate*8));raw=bytes(u.mem_read(a,52))
   out['captures'].append({'phase':state['phase'],'ms':s.now_ms(),'notes':notes,'raw':raw.hex(),'native_base_gate':basegate,'source_gate_fixture_multiplier':8,'native_timestamp':v[9],'clock':now})
   if state['phase'].startswith('UP'):
    state['active']={'notes':sorted(set(notes)),'index':0,'template':raw,'next':now,'interval':basegate*2,'gate':basegate//2,'expiry':(v[9]+basegate*16)&0xffffffff}
    # Suppress only the source chord's simultaneous emission. The guest retires
    # its original descriptor normally; generated descriptors have PC ownership.
    u.mem_write(a+0x10,bytes(4));emit(u,a,now)
  elif state['active'] and kind==3 and due(now,state['active']['next']):emit(u,a,now)
 def retire(u,pc,n,d):
  if u.reg_read(UC_M68K_REG_A2)==ARENA:
   successor=rd(u,ARENA+0x30);u.reg_write(UC_M68K_REG_D2,successor);u.reg_write(UC_M68K_REG_PC,0x400f49cc)
 s.at(0x400f40b4,queue);s.at(0x400f49c0,retire)
''' +p[z:]
p=p.replace("s=Session(case", "ARENA=0x47be6000\nstate={'phase':'setup','active':None}\ns=Session(case")
a=p.index(" s.tap(s.code('RECORD'),hold_ms=100,after_ms=100);s.tap(s.code('1')")
z=p.index(" out['halted']=",a)
p=p[:a]+''' mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
 gate=rd(s.m.uc,0x41368d64);s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3));channel=rd(s.m.uc,0x41368d2c)&15
 out['input_gate_fixture']={'before':gate,'after':gate|3};out['auto_channel']=channel+1
 def send(data):
  for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,byte)
  mi.received+=len(data);s.run_ms(35)
 # Native MIDI input and grid recording create the chord; no host-supplied notes
 # are written to the queued descriptor or stored sequencer chord.
 s.tap(s.code('RECORD'),hold_ms=70,after_ms=70);s.press(s.code('1'));s.run_ms(70)
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
 send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.release(s.code('1'));s.run_ms(70);s.tap(s.code('RECORD'),hold_ms=70,after_ms=70)
 mark('native three-note trig programmed')
 for phase,duration in [('OFF',1300),('UP_release',1500),('UP_stop',340)]:
  state['phase']=phase;state['active']=None;begin=s.now_ms();startwire=len(out['wire']);s.tap(s.code('PLAY'),hold_ms=70,after_ms=duration);before_stop=s.now_ms();s.tap(s.code('STOP'),hold_ms=70,after_ms=500)
  out['phases'].append({'phase':phase,'begin_ms':begin,'stop_request_ms':before_stop,'end_ms':s.now_ms(),'wire':out['wire'][startwire:],'active_scheduler_at_end':state['active'] is not None});mark(phase+' complete')
 out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
''' +p[z:]
p=p.replace('Digitone-E08-MIDI-track-queue-trace.json','Digitone-E08-M1-PC-prototype.json')
Path('work/test-E08-M1-PC-prototype.py').write_text(p)
