"""Observe actual stock transition while panel notes remain held. PC only."""
import pathlib,json,struct,collections,traceback,time
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('\ndef run(mode):')[0])
OUT=pathlib.Path('outputs/Digitone-MIDI-byte-debug.json')
from emu import midi
mi=midi.MidiIn()
result={'firmware_modified':False,'events':[],'marks':[],'failure':None,
        'limitations':['Untimed native run; MIDI bytes and input-enable setting are explicit PC fixtures, actual parser/CC64 handler execute.','No synthetic context injection in this stock run.']}
session=None
def state(uc):
 p=rd(uc,0x41342150)
 return {'backing':hex(p),'sequencer_position_bytes':bytes(uc.mem_read(0x41342148,2)).hex(),
         'backing_hash':hashlib.sha256(bytes(uc.mem_read(p,4*0x3d0))).hexdigest(),
         'held_mask':hex(rd(uc,0x80003fac)),
         'sustain_flags':bytes(uc.mem_read(0x41962008,8)).hex(),
         'sustain_lists':[hex(rd(uc,0x41962010+i*8)) for i in range(8)]}
def install(s):
 generations=collections.Counter();pending={}
 def cc(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7)
  result['events'].append({'kind':'CC_handler','ms':s.now_ms(),'arguments':list(struct.unpack('>5I',uc.mem_read(sp+4,20)))})
 s.at(0x400dea02,cc)
 for pc in [0x400025c8,0x40002618,0x400db1ec,0x400db256]:
  s.at(pc,lambda uc,pc,n,d:result['events'].append({'kind':'MIDI_byte_trace','ms':s.now_ms(),'pc':hex(pc),'callback':hex(uc.reg_read(UC_M68K_REG_A0)),'byte':uc.reg_read(UC_M68K_REG_D1),'ring_base':hex(rd(uc,0x404db5dc)),'read_index':rd(uc,0x404db5fc),'VBR':hex(s.m.ctlregs.get(0x801,0x40000000)),'vector':hex(rd(uc,s.m.ctlregs.get(0x801,0x40000000)+156*4))}))
 s.at(0x400db2ac,lambda uc,pc,n,d:result['events'].append({'kind':'DIN_dispatch','ms':s.now_ms(),'handler':hex(uc.reg_read(UC_M68K_REG_A0)),'stack':bytes(uc.mem_read(uc.reg_read(UC_M68K_REG_A7),16)).hex()}))
 s.at(0x400f065c,lambda uc,pc,n,d:pending.pop(rd(uc,uc.reg_read(UC_M68K_REG_A7)+4),None))
 def allocator(uc,pc,n,d):
  event=uc.reg_read(UC_M68K_REG_A0)
  if event:
   generations[event]+=1;pending.pop(event,None)
 def published(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);event=rd(uc,sp+4)
  item={'kind':'queue_publish','ms':s.now_ms(),'event':hex(event),'generation':generations[event],
        'fields':list(struct.unpack('>18I',uc.mem_read(event,72))),**state(uc)}
  pending[event]=item;result['events'].append(item)
 s.at(0x400f065a,allocator);s.at(0x400f07ac,published)
 def pointer_write(uc,access,a,n,value,d):
  if a==0x41342150:
   result['events'].append({'kind':'backing_write','ms':s.now_ms(),'pc':hex(uc.reg_read(UC_M68K_REG_PC)),
    'incoming_backing':hex(value),**state(uc),'pending_publications':list(pending.values()),'stack':bytes(uc.mem_read(uc.reg_read(UC_M68K_REG_A7),64)).hex()})
 s.m.uc.hook_add(UC_HOOK_MEM_WRITE,pointer_write,begin=0x41342150,end=0x41342153)
 def log(uc,pc,n,d,label):
  item={'kind':label,'ms':s.now_ms(),'pc':hex(pc),**state(uc)}
  if label=='publish':item['incoming_backing']=hex(uc.reg_read(UC_M68K_REG_A2))
  if label in ('producer','acceptance','pitch'):
   e=uc.reg_read(UC_M68K_REG_A2 if label=='producer' else UC_M68K_REG_A3)
   item.update(event=hex(e),track=rd(uc,e+8),type=rd(uc,e),event_state=rd(uc,e+4),identity=hex(rd(uc,e+64)),generation=generations[e])
   if label=='producer':item.update(producer_track=uc.reg_read(UC_M68K_REG_D4),producer_backing=hex(uc.reg_read(UC_M68K_REG_A3)))
   if label=='acceptance':item['publication']=pending.pop(e,None)
  result['events'].append(item)
 for pc,label in [(0x40094652,'publish'),(0x40095bd6,'transition_commit_done'),(0x40093ef4,'producer'),(0x4009dd80,'acceptance'),(0x4009df9a,'pitch')]:
  s.at(pc,lambda uc,pc,n,d,label=label:log(uc,pc,n,d,label))
def send_midi(data):
 mi.put(bytes(data))
 for i in range(20):
  if mi.deliver(session.m):session.pc=session.m.uc.reg_read(UC_M68K_REG_PC)
  session.run_ms(2)
  if mi.delivered==mi.received:break
 result.setdefault('MIDI_delivery',[]).append({'ms':session.now_ms(),'pc':hex(session.pc),'transport':rd(session.m.uc,profile.transport_state),'TCD36':bytes(session.m.uc.mem_read(midi.TCD36,32)).hex(),'bytes':bytes(data).hex(),'delivered':mi.delivered,'received':mi.received,'raised':mi.raised})
def mark(label):
 result['marks'].append({'label':label,'ms':session.now_ms(),**state(session.m.uc)})
 OUT.write_text(json.dumps(result,indent=2));print(label,session.now_ms(),result['marks'][-1]['backing'],flush=True)
try:
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=install)
 mark('initial');session.tap(session.code('PLAY'),hold_ms=40,after_ms=100)
 for t in ('T1','T2','T3','T4'):
  session.tap(session.code(t),hold_ms=20,after_ms=20)
  session.press(session.code('1'));session.run_ms(30)
  session.release(session.code('1'));session.run_ms(20)
 session.press(session.code('1'));session.press(session.code('5'));session.run_ms(50);mark('held before request')
 session.m.uc.mem_write(0x4131ba1c,u32(rd(session.m.uc,0x4131ba1c)|2))
 channel=rd(session.m.uc,0x4131b9e4)&15
 result['input_setting_fixture']={'address':'0x4131ba1c','DIN_enable_bit':2,'auto_channel_zero_based':channel}
 send_midi([0xb0|channel,64,127]);send_midi([0x90|channel,60,100]);session.run_ms(40)
 send_midi([0x80|channel,60,0]);session.run_ms(40);mark('note off while CC64 remains on')
 session.press(session.code('PTN'));session.run_ms(40)
 session.tap(session.code('2'),hold_ms=50,after_ms=40);session.release(session.code('PTN'));mark('request queued')
 for i in range(2):
  session.run_ms(250);mark('waiting '+str(i))
  if result['marks'][-1]['backing']!=result['marks'][0]['backing']:break
 mark('after actual transition')
 session.release(session.code('1'));session.release(session.code('5'));session.run_ms(300);mark('released after transition');send_midi([0xb0|channel,64,0]);session.run_ms(100);mark('CC64 released after handoff')
 session.tap(session.code('STOP'),hold_ms=30,after_ms=100)
 result['halted']=session.halted;result['inputs']=session.inputs
 result['firmware_sha256']=hashlib.sha256(SYX.read_bytes()).hexdigest()
except BaseException as e:
 result['failure']={'message':str(e),'traceback':traceback.format_exc()};print(result['failure'],flush=True)
finally:
 if session:session.close()
 OUT.write_text(json.dumps(result,indent=2))
