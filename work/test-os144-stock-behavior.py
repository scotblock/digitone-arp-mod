"""Observe stock 1.44 execution. No custom firmware code or metadata hooks."""
from pathlib import Path
exec(Path('work/os144-stock-env.py').read_text())
import json,collections,traceback,time
from emu.session import Session
from emu import midi
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
MAP=json.loads(Path('work/os144/stock-probe-map.json').read_text())
sites={k:int(v['new'],16) for k,v in MAP['sites'].items()}
CURRENT=0x4138f214;FLAGS=0x419afff4;LISTS=0x419afffc
OUT=Path('outputs/Digitone-OS1.44-stock-behavior.json')
r={'firmware_modified':False,'custom_arp_hooks_installed':False,'events':[],'marks':[],'failure':None,'fixtures':[], 'limits':['Functional session uses emulator float/bitmap shortcuts and device/storage stand-ins.','Timers use instruction pacing, not verified physical cycle timing.','MIDI input-enable RAM setting is a disclosed PC fixture; actual MIDI parser and CC64 handler execute.','A finite scenario is coverage, not exhaustive queue/lifetime proof.']}
start=time.monotonic();session=None;generations=collections.Counter();pending={};counts=collections.Counter()
def state(uc):
 p=rd(uc,CURRENT)
 return {'backing':hex(p),'backing_hash':hashlib.sha256(bytes(uc.mem_read(p,4*0x3d0))).hexdigest(),'sustain_flags':bytes(uc.mem_read(FLAGS,8)).hex(),'sustain_lists':[hex(rd(uc,LISTS+i*8)) for i in range(8)]}
def record(kind,uc,**kw):
 counts[kind]+=1;r['events'].append({'kind':kind,'ms':session.now_ms(),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),**kw})
def install(s):
 def alloc(uc,pc,n,d):
  event=uc.reg_read(UC_M68K_REG_A0)
  if event:generations[event]+=1;pending.pop(event,None)
  counts['allocated_return']+=1
 def release(uc,pc,n,d):
  event=rd(uc,uc.reg_read(UC_M68K_REG_A7)+4)
  if event in pending:record('queued_event_released',uc,event=hex(event),generation=generations[event],publication=pending.pop(event))
 def publish(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);e=rd(uc,sp+4)
  item={'event':hex(e),'generation':generations[e],'timestamp':rd(uc,sp+8),'fields':list(struct.unpack('>18I',uc.mem_read(e,72))),**state(uc)}
  pending[e]=item;record('queue_publish',uc,**item)
 def eventpoint(kind,reg):
  def hook(uc,pc,n,d):
   e=uc.reg_read(reg);item={'event':hex(e),'generation':generations[e],'fields':list(struct.unpack('>18I',uc.mem_read(e,72))),**state(uc)}
   if kind=='acceptance':item['publication']=pending.pop(e,None)
   if kind=='producer':item.update(producer_track=uc.reg_read(UC_M68K_REG_D4),producer_backing=hex(uc.reg_read(UC_M68K_REG_A3)))
   if kind=='pitch':item['coarse_pitch']=uc.reg_read(UC_M68K_REG_D6)
   record(kind,uc,**item)
  return hook
 s.at(sites['allocated_return'],alloc);s.at(sites['release'],release);s.at(sites['queue_publish'],publish)
 for label,reg in [('producer',UC_M68K_REG_A2),('acceptance',UC_M68K_REG_A3),('pitch',UC_M68K_REG_A3)]:s.at(sites[label],eventpoint(label,reg))
 def patternwrite(uc,access,addr,size,value,d):
  record('pattern_pointer_write',uc,incoming=hex(value),pending_publications=list(pending.values()),**state(uc))
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,patternwrite,begin=CURRENT,end=CURRENT+3)
 for label in ['pattern_publish','transition_done','sustain_on','sustain_release']:
  s.at(sites[label],lambda uc,pc,n,d,label=label:record(label,uc,**state(uc)))
 s.at(sites['cc_handler'],lambda uc,pc,n,d:record('CC_handler',uc,arguments=list(struct.unpack('>5I',uc.mem_read(uc.reg_read(UC_M68K_REG_A7)+4,20)))))
 s.at(0x4009e694,lambda uc,pc,n,d:record('selector_return',uc,return_d0=uc.reg_read(UC_M68K_REG_D0),return_a0=hex(uc.reg_read(UC_M68K_REG_A0))))
def persist():
 r['counts']=dict(counts);r['elapsed_seconds']=round(time.monotonic()-start,2);OUT.write_text(json.dumps(r,indent=2))
def mark(label):
 r['marks'].append({'label':label,'ms':session.now_ms(),**state(session.m.uc)});persist();print(label,round(session.now_ms(),2),r['marks'][-1]['backing'],r['marks'][-1]['sustain_flags'],dict(counts),flush=True)
def send(data,label):
 for i,byte in enumerate(data):mi._push(session.pits.now+(i+1)*session.ips*0.00032,byte)
 mi.received+=len(data);session.run_ms(20)
 r.setdefault('midi_deliveries',[]).append({'label':label,'bytes':bytes(data).hex(),'received':mi.received,'delivered':mi.delivered,'raised':mi.raised});mark(label)
try:
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=install)
 mi=midi.MidiIn();mi.attach(session.m,session.ips);session.sources=session.sources+(mi,)
 mark('settled initial');session.tap(session.code('PLAY'),hold_ms=40,after_ms=100)
 for track in ['T1','T2','T3','T4']:
  session.tap(session.code(track),hold_ms=20,after_ms=20)
  session.press(session.code('1'));session.run_ms(30);session.release(session.code('1'));session.run_ms(30);mark(track+' press consume release')
 setting=0x41368d64;before=rd(session.m.uc,setting);session.m.uc.mem_write(setting,u32(before|3))
 channel=rd(session.m.uc,0x41368d2c)&15
 r['fixtures'].append({'kind':'MIDI input enable','address':hex(setting),'before':hex(before),'after':hex(before|3),'auto_channel_zero_based':channel})
 send([0xb0|channel,64,127],'CC64 on');send([0x90|channel,60,100],'MIDI note on');session.run_ms(40)
 send([0x80|channel,60,0],'MIDI note off with sustain held');session.run_ms(80);mark('sustained before pattern request')
 session.press(session.code('1'));session.press(session.code('5'));session.run_ms(50)
 session.press(session.code('PTN'));session.run_ms(40);session.tap(session.code('2'),hold_ms=50,after_ms=40);session.release(session.code('PTN'));mark('pattern request sent')
 initial=r['marks'][0]['backing'];changed=False
 for i in range(20):
  session.run_ms(250);mark('handoff wait '+str(i))
  if hex(rd(session.m.uc,CURRENT))!=initial:changed=True;break
 mark('after handoff observation');session.release(session.code('1'));session.release(session.code('5'));session.run_ms(200)
 send([0xb0|channel,64,0],'CC64 off after handoff');session.run_ms(200);mark('release settled')
 session.tap(session.code('1'),hold_ms=40,after_ms=80);mark('fresh note after handoff')
 session.tap(session.code('STOP'),hold_ms=30,after_ms=100);mark('stopped')
 r['halted']=session.halted;r['inputs']=session.inputs;r['audio_bytes']=len(session.pcm);r['audio_sha256']=hashlib.sha256(session.pcm).hexdigest()
 accepted=[e for e in r['events'] if e['kind']=='acceptance' and e.get('publication')]
 r['checks']={'no_engine_halt':session.halted is None,'queue_publish_observed':counts['queue_publish']>0,'same_generation_publish_to_acceptance':bool(accepted) and all(e['generation']==e['publication']['generation'] for e in accepted),'pitch_output_observed':counts['pitch']>0,'pattern_backing_changed':changed,'pattern_publish_observed':counts['pattern_publish']>0,'transition_done_observed':counts['transition_done']>0,'CC64_handler_observed':counts['CC_handler']>0,'sustain_on_path_observed':counts['sustain_on']>0,'sustain_release_path_observed':counts['sustain_release']>0,'all_midi_bytes_delivered':mi.received==mi.delivered}
 r['cross_pattern_acceptances']=[e for e in accepted if e['backing']!=e['publication']['backing']]
except BaseException:
 r['failure']=traceback.format_exc();print(r['failure'],flush=True)
finally:
 if session:session.close()
 r['firmware_sha256_after']=hashlib.sha256(SYX.read_bytes()).hexdigest();persist()
