"""Extend confirmed queued/MIDI-sustain coverage through actual native transition."""
import pathlib,os
source=pathlib.Path('work/test-combined-queued-sustained-handoff.py').read_text()
line=next(x for x in source.splitlines() if x.startswith('exec(pathlib.Path'))
source=source.replace(line,"exec(pathlib.Path('work/indexed-context-environment.py').read_text())")
mode=os.environ.get('HANDOFF_MODE','all');assert mode in ['all','stock']
scaled=os.environ.get('SCALE_HANDOFF')=='1';suffix=mode+('-scaled' if scaled else '')
source=source.replace('outputs/Digitone-queued-sustained-combined-handoff.json',f'outputs/Digitone-indexed-context-handoff-{suffix}.json')
source=source.replace(" generations=collections.Counter();pending={};delayed=False",''' uc=s.m.uc
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
 result['_guards']=bytes(uc.mem_read(RAM,0x20000)).hex()
 if MODE=='stock':
  for pc,n in [(0x40093ef4,8),(0x400f0626,6),(0x4009dda6,6),(0x4009de46,10),(0x4009df9a,8)]:uc.mem_write(pc,stock[pc-base:pc-base+n])
 def storage_write(uc,access,address,n,value,d):
  physical=0x40000000+(address-0x40000000)%DDR
  if not (physical<RAM+0x20000 and RAM<physical+n):return
  pc=uc.reg_read(UC_M68K_REG_PC)
  if PTR<=physical and physical+n<=BSS+0xb70 and RAM<=pc<RAM+1892:return
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
 generations=collections.Counter();pending={};delayed=False''')
source=source.replace("'timestamp':rd(uc,sp+8),'fields'", "'metadata':hex(rd(uc,BSS+32+(event-0x4199da94)//72*4)) if 0<=event-0x4199da94<128*72 and (event-0x4199da94)%72==0 else None,'timestamp':rd(uc,sp+8),'fields'")
source=source.replace(" result['halted']=session.halted;result['inputs']=session.inputs",''' now=bytes(session.m.uc.mem_read(RAM,0x20000));guard=bytes.fromhex(result.pop('_guards'));excluded=set(range(PTR-RAM,BSS+0xb70-RAM))
 result['storage_checks']={'helper_intact':now[:len(blob)]==blob,'guards_intact':all(now[i]==guard[i] for i in range(len(now)) if i not in excluded),'no_unexpected_guest_writes':not result['unexpected_storage_writes']}
 assert all(result['storage_checks'].values())
 result['halted']=session.halted;result['inputs']=session.inputs''')
source=source.replace(" session.run_ms(1000);mark('queued note observation after handoff')", " session.run_ms(2000);mark('queued note observation after handoff')")
source=source.replace("if label=='acceptance':item['publication']=pending.pop(e,None)","if label=='acceptance':\n    item['candidate_at_acceptance']=hex(rd(uc,BSS+32+(e-0x4199da94)//72*4)) if 0<=e-0x4199da94<128*72 and (e-0x4199da94)%72==0 else None\n    item['publication']=pending.pop(e,None)")
exec(compile('MODE='+repr(mode)+'\nSCALED='+repr(scaled)+'\n'+source,'indexed-context-handoff','exec'))


