from pathlib import Path
import sys,os,json,struct,time,traceback
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootstrap as bs,longrun,midi
from emu.session import Session
from unicorn.m68k_const import *
from unicorn import UC_HOOK_MEM_WRITE
original=longrun.build
def build(*args,**kwargs):kwargs['unblock']=False;return original(*args,**kwargs)
longrun.build=build
syx=Path('work/os144/E07-PC-candidate.syx').resolve();case=next(r for r in json.loads(Path('outputs/Digitone-E07-PC-startup-comparison.json').read_text())['cases'] if r['image']=='E07_restored');root=Path(case['ui_snapshot']).parents[2]
paths=bs.FirmwarePaths(str(root),syx.name,str(Path('work/upstream/digiemu/devices').resolve()));os.environ.update(paths.env())
cfg=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text());payload=Path('work/os144/E07-PC-payload.bin').read_bytes();out={'PC_only':True,'firmware_unchanged':True,'prototype_kind':'Host-assisted PC scheduler feeding native guest MIDI task; not a machine-code patch','events':[],'wire':[],'marks':[],'failure':None,'counts':{},'queue_counts':{},'queue_samples':[],'phases':[],'captures':[],'generations':[],'cancellations':[],'clock_samples':[],'live_inputs':[]}
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'big')
def install(s):
 for r in cfg['regions']:
  if r['base']>=0x47be0000:s.m.install_isa_patches_scoped(payload[r['base']-0x47be0000:r['base']-0x47be0000+r['bytes']],r['base'])
 def driver(u,pc,n,d):
  sp=u.reg_read(UC_M68K_REG_A7);args=[rd(u,sp+i*4) for i in range(7)]
  event={'ms':s.now_ms(),'pc':hex(pc),'stack':[hex(x) for x in args],'registers':[hex(u.reg_read(UC_M68K_REG_D0+i)) for i in range(8)]}
  if pc in [0x40002a3a,0x400f3e70] and 0<args[1]<512:event['buffer']=list(u.mem_read(args[2],args[1]))
  key=hex(pc);out['counts'][key]=out['counts'].get(key,0)+1
  if out['counts'][key]<=24:out['events'].append(event)
 for pc in [0x40002a3a,0x40002b6e,0x40002c08,0x400eabb4,0x400eae5c,0x400edbc2,0x400f3e70,0x400f3c1a,0x400f3c4a,0x400f4dd0,0x400f2c00,0x400f0580,0x40097e46,0x40098116]:s.at(pc,driver)
 s.m.ensure(ARENA)
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
   if kind==4 or (not state['active'].get('live') and s.profile.transport_state and rd(u,s.profile.transport_state)!=1):
    out['cancellations'].append({'phase':state['phase'],'reason':'native_stop_dispatch' if kind==4 else 'native_transport_stopped','ms':s.now_ms()});state['active']=None
   elif state['active']['expiry'] is not None and due(now,state['active']['expiry']):
    out['cancellations'].append({'phase':state['phase'],'reason':'source_gate_expired','ms':s.now_ms()});state['active']=None
  if state['phase']=='UP_live_release' and kind in [0,1] and v[1]==0 and v[11]==2 and v[4]==1:
   raw=bytes(u.mem_read(a,52));note=raw[0x14];on=v[2]==1;held=state.setdefault('held',set())
   out['live_inputs'].append({'ms':s.now_ms(),'note':note,'on':on,'raw':raw.hex()})
   if on:
    held.add(note)
    if state['active'] is None:state['active']={'notes':sorted(held),'index':0,'template':raw,'next':now,'interval':5400000,'gate':1350000,'expiry':None,'live':True}
    else:state['active']['notes']=sorted(held)
    u.mem_write(a+0x10,bytes(4))
   else:
    held.discard(note)
    if not held:
     out['cancellations'].append({'phase':state['phase'],'reason':'native_source_key_release','ms':s.now_ms()});state['active']=None
    elif state['active']:state['active']['notes']=sorted(held)
   return
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
 mo=midi.MidiOut(lambda data:out['wire'].append({'ms':s.now_ms(),'bytes':list(data)}));mo.install(s.m);mo.attach(s.m,s.ips);s.sources=s.sources+(mo,);s.midi_mirror_observer=mo
ARENA=0x47be6000
state={'phase':'setup','active':None}
s=Session(case['ui_snapshot'],syx=str(syx),ddr=0x08000000,on_machine=install)
def mark(label):
 out['marks'].append({'label':label,'ms':s.now_ms(),'pc':hex(s.pc),'wire_bytes':s.midi_mirror_observer.sent});print(label,'ms',s.now_ms(),'wire',s.midi_mirror_observer.sent,flush=True)
try:
 for _ in range(10):
  s.run_ms(1000)
  if s.ev['dsplink'].booted and s.ev['dsplink'].renders>100:break
 mark('warm')
 s.tap(s.code('STOP'),hold_ms=100,after_ms=100)
 s.press(s.code('MIDI'));s.tap(s.code('T1'),hold_ms=100,after_ms=100);s.release(s.code('MIDI'));s.run_ms(200)
 s.tap(s.code('SYN1'),hold_ms=100,after_ms=100)
 # Native UI: enable MIDI source channel with FUNC + encoder A, then channel 1.
 s.press(s.code('FUNC'));s.tap(s.code('A'),hold_ms=100,after_ms=100);s.release(s.code('FUNC'));s.run_ms(200)
 mark('MIDI track source channel enabled')
 mi=midi.MidiIn();mi.attach(s.m,s.ips);s.sources=s.sources+(mi,)
 gate=rd(s.m.uc,0x41368d64);s.m.uc.mem_write(0x41368d64,struct.pack('>I',gate|3));channel=rd(s.m.uc,0x41368d2c)&15
 out['input_gate_fixture']={'before':gate,'after':gate|3};out['auto_channel']=channel+1
 def send(data):
  for i,byte in enumerate(data):mi._push(s.pits.now+(i+1)*s.ips*0.00032,byte)
  mi.received+=len(data);s.run_ms(35)
 state['phase']='UP_live_release';begin=s.now_ms();startwire=len(out['wire'])
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
 for _ in range(80):
  count=sum(1 for x in out['wire'][startwire:] for i in range(0,len(x['bytes']),3) if x['bytes'][i]&240==144 and x['bytes'][i+2]>0)
  if count>=3:break
  s.run_ms(10)
 assert count>=3,'live arp did not emit three notes'
 s.run_ms(10);release_request=s.now_ms()
 send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(450)
 out['phases'].append({'phase':'UP_live_release','begin_ms':begin,'release_request_ms':release_request,'end_ms':s.now_ms(),'wire':out['wire'][startwire:],'active_scheduler_at_end':state['active'] is not None,'held_at_end':sorted(state.get('held',[]))});mark('live source release complete')
 out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
 out['halted']=s.halted
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 s.close();Path('outputs/Digitone-E08-M1-PC-live-release.json').write_text(json.dumps(out,indent=2))
