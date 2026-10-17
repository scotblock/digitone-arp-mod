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
cfg=json.loads(Path('outputs/Digitone-E07-PC-candidate-layout.json').read_text());payload=Path('work/os144/E07-PC-payload.bin').read_bytes();out={'PC_only':True,'firmware_unchanged':True,'prototype_kind':'Native ColdFire scheduler, consumer and retirement hooks; host configuration/input fixtures only','events':[],'wire':[],'marks':[],'failure':None,'counts':{},'queue_counts':{},'queue_samples':[],'phases':[],'captures':[],'generations':[],'cancellations':[],'clock_samples':[],'native_helper_observations':[]}
native=json.loads(Path('work/os144/E08-PC-native-M1-layout.json').read_text());native_blob=Path('work/os144/E08-PC-native-M1-code.bin').read_bytes()
from emu.harness import call as native_call

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
 for address in [native['base'],native['state'],native['arena'],0x47be7f00]:s.m.ensure(address)
 s.m.uc.mem_write(native['base'],native_blob)
 for r in native['regions']:
  s.m.install_isa_patches_scoped(native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']],r['base'])
 for h in native['hooks']:
  assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['original'],h
  s.m.uc.mem_write(h['site'],bytes.fromhex(h['replacement']))
 regs=list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC]
 saved={reg:s.m.uc.reg_read(reg) for reg in regs}
 native_call(s.m,native['entries']['init'],[s.profile.transport_state],stack_top=0x47be7f00,limit=30000)
 s.m.uc.reg_write(UC_M68K_REG_SR,saved[UC_M68K_REG_SR])
 for reg,value in saved.items():
  if reg!=UC_M68K_REG_SR:s.m.uc.reg_write(reg,value)
 assert rd(s.m.uc,native['state'])==0x4d314131
 out['native_initialization_executed']=True
 def queue_observe(u,pc,n,d):
  a=u.reg_read(UC_M68K_REG_A2)
  if a==native['arena']:return
  v=[rd(u,a+i*4) for i in range(13)]
  if state['phase'] in ['OFF','UP_release','UP_stop'] and v[0] in [0,1] and v[1]==0 and v[2]==1 and v[4]>=3:
   assert v[7]>0
   u.mem_write(a+0x1c,struct.pack('>I',v[7]*8))
   out['captures'].append({'phase':state['phase'],'ms':s.now_ms(),'notes':list(u.mem_read(a+20,v[4])),'native_base_gate':v[7],'source_gate_fixture_multiplier':8})
 s.at(0x400f40b4,queue_observe)
 def observe(u,pc,n,d):
  if len(out['native_helper_observations'])<100:out['native_helper_observations'].append({'phase':state['phase'],'pc':hex(pc),'ms':s.now_ms(),'active':rd(u,native['state']+8),'count':rd(u,native['state']+16)})
 for entry in [native['entries']['emit'],native['entries']['retire']]:s.at(entry,observe)
 mo=midi.MidiOut(lambda data:out['wire'].append({'ms':s.now_ms(),'bytes':list(data)}));mo.install(s.m);mo.attach(s.m,s.ips);s.sources=s.sources+(mo,);s.midi_mirror_observer=mo
ARENA=0x47be6000
state={'phase':'setup'}
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
 # Native MIDI input and grid recording create the chord; no host-supplied notes
 # are written to the queued descriptor or stored sequencer chord.
 s.tap(s.code('RECORD'),hold_ms=70,after_ms=70);s.press(s.code('1'));s.run_ms(70)
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
 send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.release(s.code('1'));s.run_ms(70);s.tap(s.code('RECORD'),hold_ms=70,after_ms=70)
 mark('native three-note trig programmed')
 for phase,duration in [('OFF',1300),('UP_release',1500),('UP_stop',340)]:
  state['phase']=phase;s.m.uc.mem_write(native['state']+4,struct.pack('>I',0 if phase=='OFF' else 1));begin=s.now_ms();startwire=len(out['wire']);s.tap(s.code('PLAY'),hold_ms=70,after_ms=duration);before_stop=s.now_ms();s.tap(s.code('STOP'),hold_ms=70,after_ms=500)
  out['phases'].append({'phase':phase,'begin_ms':begin,'stop_request_ms':before_stop,'end_ms':s.now_ms(),'wire':out['wire'][startwire:],'active_scheduler_at_end':rd(s.m.uc,native['state']+8)!=0,'native_counters':[rd(s.m.uc,native['state']+i) for i in [48,52,56,60]],'arena_busy_at_end':rd(s.m.uc,native['state']+280)});mark(phase+' complete')
 state['phase']='UP_live_release';begin=s.now_ms();startwire=len(out['wire']);live_inputs_before=mi.delivered
 send([0x90|channel,60,100,0x90|channel,64,100,0x90|channel,67,100])
 for _ in range(80):
  count=sum(1 for x in out['wire'][startwire:] for i in range(0,len(x['bytes']),3) if x['bytes'][i]&240==144 and x['bytes'][i+2]>0)
  if count>=3:break
  s.run_ms(10)
 assert count>=3,'native live arp did not emit three notes'
 s.run_ms(10);release_request=s.now_ms()
 send([0x80|channel,60,0,0x80|channel,64,0,0x80|channel,67,0]);s.run_ms(450)
 out['phases'].append({'phase':'UP_live_release','begin_ms':begin,'release_request_ms':release_request,'end_ms':s.now_ms(),'wire':out['wire'][startwire:],'active_scheduler_at_end':rd(s.m.uc,native['state']+8)!=0,'native_counters':[rd(s.m.uc,native['state']+i) for i in [48,52,56,60]],'arena_busy_at_end':rd(s.m.uc,native['state']+280),'native_held_count_at_end':rd(s.m.uc,native['state']+16)});mark('native live release complete')
 for h in native['hooks']:assert bytes(s.m.uc.mem_read(h['site'],h['length'])).hex()==h['replacement']
 for r in native['regions']:assert bytes(s.m.uc.mem_read(r['base'],r['bytes']))==native_blob[r['base']-native['base']:r['base']-native['base']+r['bytes']]
 out['native_code_preserved']=True;out['native_state_final']=bytes(s.m.uc.mem_read(native['state'],320)).hex()
 out['MIDI_received']=mi.received;out['MIDI_delivered']=mi.delivered
 out['halted']=s.halted
except Exception:out['failure']=traceback.format_exc();print(out['failure'],flush=True)
finally:
 s.close();Path('outputs/Digitone-E08-M1-native-playback.json').write_text(json.dumps(out,indent=2))
