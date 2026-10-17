CACHE_MODE='fixed'
MODE='all'
SCALED=True
"""Observe actual stock transition while panel notes remain held. PC only."""
import pathlib,json,struct,collections,traceback,time
exec(pathlib.Path('work/indexed-context-environment.py').read_text())
OUT=pathlib.Path('outputs/Digitone-indexed-context-handoff-cache-context-fresh-settings.json')
from emu import midi
mi=midi.MidiIn()
result={'firmware_modified':False,'events':[],'marks':[],'failure':None,
        'limitations':['Untimed native run; MIDI bytes and input-enable setting are explicit PC fixtures, actual parser/CC64 handler execute.','One actual stock-produced note is explicitly delayed at queue publication in PC RAM. No context metadata injected; native transition and consumers execute.']}
session=None
def state(uc):
 p=rd(uc,0x41342150)
 return {'backing':hex(p),'sequencer_position_bytes':bytes(uc.mem_read(0x41342148,2)).hex(),
         'backing_hash':hashlib.sha256(bytes(uc.mem_read(p,4*0x3d0))).hexdigest(),
         'held_mask':hex(rd(uc,0x80003fac)),
         'sustain_flags':bytes(uc.mem_read(0x41962008,8)).hex(),
         'sustain_lists':[hex(rd(uc,0x41962010+i*8)) for i in range(8)]}
def install(s):
 uc=s.m.uc
 assert bytes(uc.mem_read(RAM,len(blob)))==blob
 assert rd(uc,PTR)==BSS-0x14100 and list(struct.unpack('>IIII',uc.mem_read(BSS,16)))==[0x534c4332,2,0xb70,1]
 s.m.install_isa_patches_scoped(blob[:1892],RAM)
 result['mode']=MODE;result['startup_source']='outputs/Digitone-indexed-context-startup-playback.json'
 result['helper_reinjected']=False;result['quantizer_calls']=[];result['pitch_outputs']=[];result['unexpected_storage_writes']=[]
 result['pitch_serial']=0
 if SCALED:
  old=rd(uc,0x41342150);new=0x407c61e9
  result['root_scale_fixture']={'old_backing':hex(old),'new_backing':hex(new),'old_root':59,'old_raw_scale':5,'new_root':61,'new_raw_scale':0,'metadata_injection':False}
  for backing,root,raw in [(old,59,5),(new,61,0)]:
   for track in range(4):
    uc.mem_write(backing+track*0x3d0+0x3cb,bytes([root]));uc.mem_write(backing+track*0x3d0+0x3ce,bytes([raw]))

 result['cache_context_mode']=CACHE_MODE;result['cache_builds']=[];result['cache_copies']=[]
 if CACHE_MODE=='fixed':
  # global declaration supplied at install entry
  original_blob=blob;globals()['blob']=pathlib.Path('work/cache-context-overlay.bin').read_bytes()
  build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
  # Deliberately local in-memory extension after inherited stock startup;
  # this test does not certify the changed loader/copier route.
  uc.mem_write(RAM,blob);s.m.install_isa_patches_scoped(blob,RAM)
  for site in build['hooks']:
   original=bytes.fromhex('4e914fef000c' if site==0x4009344e else '4eb9400ec23c')
   assert bytes(uc.mem_read(site,6))==original
   uc.mem_write(site,bytes.fromhex('4ef9' if site==0x4009344e else '4eb9')+u32(build['first_copy_address'] if site==0x4009344e else build['copy_address']))
  result['PC_runtime_extension_installed']=True
  result['helper_reinjected']=True
 def cache_build(uc,pc,n,d):
  e=uc.reg_read(UC_M68K_REG_A2);b=uc.reg_read(UC_M68K_REG_A3);t=uc.reg_read(UC_M68K_REG_D4)
  if 0<=e-0x419a304c<288 and (e-0x419a304c)%72==0:
   root=bytes(uc.mem_read(b+t*0x3d0+0x3cb,1))[0];raw=struct.unpack('b',uc.mem_read(b+t*0x3d0+0x3ce,1))[0]
   result['cache_builds'].append({'ms':s.now_ms(),'event':hex(e),'backing':hex(b),'current_backing':hex(rd(uc,0x41342150)),'track':t,'root':root,'raw':raw,'word':hex(rd(uc,BSS+2592+(e-0x419a304c)//72*4))})
 s.at(0x40093efc,cache_build)
 def cache_copy(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);dst=rd(uc,sp);origin=rd(uc,sp+4)
  result['cache_copies'].append({'ms':s.now_ms(),'site':hex(pc),'source':hex(origin),'destination':hex(dst),'size':rd(uc,sp+8),'backing':hex(rd(uc,0x41342150)),'source_fields':list(struct.unpack('>18I',uc.mem_read(origin,72))),'source_context':hex(rd(uc,BSS+2592+(origin-0x419a304c)//72*4)) if 0<=origin-0x419a304c<288 and (origin-0x419a304c)%72==0 else None})
 for site in [0x4009344e,0x40093892]:s.at(site,cache_copy)

 result['_guards']=bytes(uc.mem_read(RAM,0x20000)).hex()
 if MODE=='stock':
  for pc,n in [(0x40093ef4,8),(0x400f0626,6),(0x4009dda6,6),(0x4009de46,10),(0x4009df9a,8)]:uc.mem_write(pc,stock[pc-base:pc-base+n])
 def storage_write(uc,access,address,n,value,d):
  physical=0x40000000+(address-0x40000000)%DDR
  if not (physical<RAM+0x20000 and RAM<physical+n):return
  pc=uc.reg_read(UC_M68K_REG_PC)
  if PTR<=physical and physical+n<=BSS+0xb70 and RAM<=pc<RAM+len(blob):return
  result['unexpected_storage_writes'].append({'pc':hex(pc),'address':hex(address),'size':n})
 for k in range(8):uc.hook_add(UC_HOOK_MEM_WRITE,storage_write,begin=RAM+k*DDR-64,end=RAM+k*DDR+0x20000+63)
 def quant(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7);note=rd(uc,sp+4);word=rd(uc,sp+8)
  e=uc.reg_read(UC_M68K_REG_A2);result['pitch_serial']+=1
  result['quantizer_calls'].append({'ms':s.now_ms(),'ordinal':result['pitch_serial'],'event':hex(e),'generation':generations[e],'note':note,'word':hex(word),'expected':oracle(note,word)})
 s.at(layout['quantize']['address'],quant)
 def output(uc,pc,n,d):
  e=uc.reg_read(UC_M68K_REG_A3);track=rd(uc,e+8);result['pitch_serial']+=1
  result['pitch_outputs'].append({'ms':s.now_ms(),'ordinal':result['pitch_serial'],'event':hex(e),'generation':generations[e],'track':track,'fixed_note':uc.reg_read(UC_M68K_REG_D6),'record':bytes(uc.mem_read(BSS+0xb30+track*16,16)).hex() if track<4 else None})
 s.at(0x4009dfa8,output)
 generations=collections.Counter();pending={};delayed=False

 result['early_event_copies']=[]
 def copy_origin(uc,pc,n,d):
  if s.now_ms()>300:return
  sp=uc.reg_read(UC_M68K_REG_A7);a=rd(uc,sp+4);b=rd(uc,sp+8)
  if not (0<=a-0x4199da94<128*72 or 0<=b-0x4199da94<128*72):return
  result['early_event_copies'].append({'ms':s.now_ms(),'return':hex(rd(uc,sp)),'args':[hex(a),hex(b)]})
 s.at(0x400f0690,copy_origin)

 def cc(uc,pc,n,d):
  sp=uc.reg_read(UC_M68K_REG_A7)
  result['events'].append({'kind':'CC_handler','ms':s.now_ms(),'arguments':list(struct.unpack('>5I',uc.mem_read(sp+4,20)))})
 s.at(0x400dea02,cc)
 for address in [0x400db246,0x400db2ac]:
  s.at(address,lambda uc,pc,n,d:result['events'].append({'kind':'input_dispatch','ms':s.now_ms(),'pc':hex(pc),'handler':hex(uc.reg_read(UC_M68K_REG_A0)),'arguments':list(struct.unpack('>3I',uc.mem_read(uc.reg_read(UC_M68K_REG_A7),12)))}))
 s.at(0x400f065c,lambda uc,pc,n,d:pending.pop(rd(uc,uc.reg_read(UC_M68K_REG_A7)+4),None))
 def allocator(uc,pc,n,d):
  event=uc.reg_read(UC_M68K_REG_A0)
  if event:
   generations[event]+=1;pending.pop(event,None)
 def published(uc,pc,n,d):
  nonlocal delayed
  sp=uc.reg_read(UC_M68K_REG_A7);event=rd(uc,sp+4)
  before=rd(uc,sp+8)
  if rd(uc,event)<2 and rd(uc,event+8)==2 and not delayed:
   delayed=True;after=(before+0)&0xffffffff;uc.mem_write(sp+8,u32(after))
   result['delayed_note_fixture']={'ms':s.now_ms(),'event':hex(event),'generation':generations[event],'before_timestamp':before,'after_timestamp':after,'added_timer_ticks':0}
  item={'kind':'queue_publish','ms':s.now_ms(),'event':hex(event),'generation':generations[event],
        'metadata':hex(rd(uc,BSS+32+(event-0x4199da94)//72*4)) if 0<=event-0x4199da94<128*72 and (event-0x4199da94)%72==0 else None,'publisher_return':hex(rd(uc,sp)),'timestamp':rd(uc,sp+8),'fields':list(struct.unpack('>18I',uc.mem_read(event,72))),**state(uc)}
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
   if label=='acceptance':
    item['candidate_at_acceptance']=hex(rd(uc,BSS+32+(e-0x4199da94)//72*4)) if 0<=e-0x4199da94<128*72 and (e-0x4199da94)%72==0 else None
    item['publication']=pending.pop(e,None)
  result['events'].append(item)
 for pc,label in [(0x40094652,'publish'),(0x40095bd6,'transition_commit_done'),(0x40093ef4,'producer'),(0x4009dd80,'acceptance'),(0x4009df9a,'pitch')]:
  s.at(pc,lambda uc,pc,n,d,label=label:log(uc,pc,n,d,label))
def send_midi(data):
 mi.received+=len(data)
 for i,byte in enumerate(data):mi._push(session.pits.now+(i+1)*session.ips*0.00032,byte)
 session.run_ms(10)
 result.setdefault('MIDI_delivery',[]).append({'ms':session.now_ms(),'bytes':bytes(data).hex(),'delivered':mi.delivered,'received':mi.received,'raised':mi.raised})
def mark(label):
 result['marks'].append({'label':label,'ms':session.now_ms(),**state(session.m.uc)})
 OUT.write_text(json.dumps(result,indent=2));print(label,session.now_ms(),result['marks'][-1]['backing'],flush=True)
try:
 session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=install)

 def select_pattern(number):
  session.press(session.code('PTN'));session.run_ms(30)
  session.tap(session.code(str(number)),hold_ms=30,after_ms=30)
  session.release(session.code('PTN'));session.run_ms(150)
 def combo(button):
  session.press(session.code('FUNC'));session.run_ms(30)
  session.tap(session.code(button),hold_ms=40,after_ms=40)
  session.release(session.code('FUNC'));session.run_ms(150)
 for track in range(4):
  session.m.uc.mem_write(0x407c61e9+track*0x3d0+0x3cb,bytes([59]))
  session.m.uc.mem_write(0x407c61e9+track*0x3d0+0x3ce,bytes([5]))
 select_pattern(2);copy_source=rd(session.m.uc,0x41342150)
 actual_old=copy_source
 result['native_pattern_preparation']={'old_backing':hex(actual_old),'native_selection':True,'copy_paste_panel_actions':False}
 result['root_scale_fixture']={'old_backing':hex(actual_old),'new_backing':'0x407b00cc','old_root':59,'old_raw_scale':5,'new_root':59,'new_raw_scale':5,'metadata_injection':False}
 for track in range(4):
  session.m.uc.mem_write(0x407b00cc+track*0x3d0+0x3cb,bytes([59]))
  session.m.uc.mem_write(0x407b00cc+track*0x3d0+0x3ce,bytes([5]))
  session.m.uc.mem_write(actual_old+track*0x3d0+0x3cb,bytes([59]))
  session.m.uc.mem_write(actual_old+track*0x3d0+0x3ce,bytes([5]))

 mi.attach(session.m,session.ips);session.sources=session.sources+(mi,);mark('initial');session.tap(session.code('PLAY'),hold_ms=40,after_ms=100)
 session.run_ms(100);mark('source playback before request')
 session.release(session.code('1'));session.press(session.code('PTN'));session.run_ms(40)
 session.tap(session.code('1'),hold_ms=50,after_ms=40);session.release(session.code('PTN'));mark('request queued')
 session.m.uc.mem_write(0x4131ba1c,u32(rd(session.m.uc,0x4131ba1c)|3))
 channel=rd(session.m.uc,0x4131b9e4)&15
 result['input_setting_fixture']={'address':'0x4131ba1c','receive_enable_bits':3,'auto_channel_zero_based':channel}
 send_midi([0xb0|channel,64,127]);send_midi([0x90|channel,60,100]);session.run_ms(40)
 send_midi([0x80|channel,60,0]);session.run_ms(40);mark('note off while CC64 remains on')

 for i in range(16):
  session.run_ms(250);mark('waiting '+str(i))
  if result['marks'][-1]['backing']!=result['marks'][0]['backing']:break
 mark('after actual transition')
 session.run_ms(2000);mark('queued note observation after handoff');session.release(session.code('1'));session.release(session.code('5'));session.run_ms(300);mark('released after transition');send_midi([0xb0|channel,64,0]);session.run_ms(100);mark('CC64 released after handoff')
 session.tap(session.code('STOP'),hold_ms=30,after_ms=100)
 now=bytes(session.m.uc.mem_read(RAM,0x20000));guard=bytes.fromhex(result.pop('_guards'));excluded=set(range(PTR-RAM,BSS+0xb70-RAM))
 result['storage_checks']={'helper_intact':now[:len(blob)]==blob,'guards_intact':all(now[i]==guard[i] for i in range(len(now)) if i not in excluded),'no_unexpected_guest_writes':not result['unexpected_storage_writes']}
 assert all(result['storage_checks'].values())
 result['halted']=session.halted;result['inputs']=session.inputs
 result['firmware_sha256']=hashlib.sha256(SYX.read_bytes()).hexdigest()
except BaseException as e:
 result['failure']={'message':str(e),'traceback':traceback.format_exc()};print(result['failure'],flush=True)
finally:
 if session:session.close()
 OUT.write_text(json.dumps(result,indent=2))
