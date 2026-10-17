"""Observe actual stock transition while panel notes remain held. PC only."""
import pathlib,json,struct,collections,traceback,time
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('\ndef run(mode):')[0])
OUT=pathlib.Path('outputs/Digitone-delayed-note-pattern-handoff.json')
result={'firmware_modified':False,'events':[],'marks':[],'failure':None,
        'limitations':['Untimed native functional run; held panel notes are not MIDI CC64 sustain.','One queue timestamp explicitly delayed in PC RAM; native queue insertion/transition/consumer execute. No synthetic metadata injection in stock run.']}
session=None
def state(uc):
 p=rd(uc,0x41342150)
 return {'backing':hex(p),'sequencer_position_bytes':bytes(uc.mem_read(0x41342148,2)).hex(),
         'backing_hash':hashlib.sha256(bytes(uc.mem_read(p,4*0x3d0))).hexdigest(),
         'held_mask':hex(rd(uc,0x80003fac))}
def install(s):
 generations=collections.Counter();pending={};delayed=False
 def allocator(uc,pc,n,d):
  event=uc.reg_read(UC_M68K_REG_A0)
  if event:
   generations[event]+=1;pending.pop(event,None)
 def published(uc,pc,n,d):
  nonlocal delayed
  sp=uc.reg_read(UC_M68K_REG_A7);event=rd(uc,sp+4)
  before=rd(uc,sp+8)
  if rd(uc,event)==0 and not delayed:
   delayed=True;after=(before+48000000)&0xffffffff
   uc.mem_write(sp+8,u32(after))
   result['delayed_note_fixture']={'ms':s.now_ms(),'event':hex(event),'generation':generations[event],'before_timestamp':before,'after_timestamp':after,'added_timer_ticks':48000000,'description':'PC fixture delays one actual stock-produced note at stock queue-publisher entry; no pattern-pointer or transition edits.'}
  item={'kind':'queue_publish','ms':s.now_ms(),'event':hex(event),'generation':generations[event],
        'timestamp':rd(uc,sp+8),'fields':list(struct.unpack('>18I',uc.mem_read(event,72))),**state(uc)}
  pending[event]=item;result['events'].append(item)
 s.at(0x400f065a,allocator);s.at(0x400f07ac,published)
 s.at(0x400f065c,lambda uc,pc,n,d:pending.pop(rd(uc,uc.reg_read(UC_M68K_REG_A7)+4),None))
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
 session.press(session.code('PTN'));session.run_ms(40)
 session.tap(session.code('2'),hold_ms=50,after_ms=40);session.release(session.code('PTN'));mark('request queued')
 for i in range(16):
  session.run_ms(250);mark('waiting '+str(i))
  if result['marks'][-1]['backing']!=result['marks'][0]['backing']:break
 mark('after actual transition')
 session.run_ms(1000);mark('queued note observation after handoff');session.release(session.code('1'));session.release(session.code('5'));session.run_ms(300);mark('released after transition')
 session.tap(session.code('STOP'),hold_ms=30,after_ms=100)
 result['halted']=session.halted;result['inputs']=session.inputs
 result['firmware_sha256']=hashlib.sha256(SYX.read_bytes()).hexdigest()
except BaseException as e:
 result['failure']={'message':str(e),'traceback':traceback.format_exc()};print(result['failure'],flush=True)
finally:
 if session:session.close()
 OUT.write_text(json.dumps(result,indent=2))
