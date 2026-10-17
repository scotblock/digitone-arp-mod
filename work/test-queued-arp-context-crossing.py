"""Delay an actual track-2 note across native replacement; no eligibility injection."""
import pathlib,os
os.environ.update(HANDOFF_MODE='all',SCALE_HANDOFF='1')
source=pathlib.Path('work/test-indexed-context-handoff.py').read_text()
label=os.environ.get('ARP_CONTROL','natural');assert label in ['natural','no-delay','forced-context']
suffix='queued-arp-crossing'+('' if label=='natural' else '-'+label)
source=source.replace("suffix=mode+('-scaled' if scaled else '')", 'suffix='+repr(suffix))
origin="""
 result['early_event_copies']=[]
 def copy_origin(uc,pc,n,d):
  if s.now_ms()>300:return
  sp=uc.reg_read(UC_M68K_REG_A7);a=rd(uc,sp+4);b=rd(uc,sp+8)
  if not (0<=a-0x4199da94<128*72 or 0<=b-0x4199da94<128*72):return
  result['early_event_copies'].append({'ms':s.now_ms(),'return':hex(rd(uc,sp)),'args':[hex(a),hex(b)]})
 s.at(0x400f0690,copy_origin)
"""
source=source.replace("exec(compile('MODE='", "source=source.replace(\" generations=collections.Counter();pending={};delayed=False\",\" generations=collections.Counter();pending={};delayed=False\\n\"+"+repr(origin)+")\nsource=source.replace(\"'timestamp':rd(uc,sp+8),'fields'\",\"'publisher_return':hex(rd(uc,sp)),'timestamp':rd(uc,sp+8),'fields'\")\nexec(compile('MODE='")
delay=0 if label=='no-delay' else 96000000
source=source.replace("exec(compile('MODE='", "source=source.replace('if rd(uc,event)==0 and not delayed:', 'if rd(uc,event)<2 and rd(uc,event+8)==2 and not delayed:')\nsource=source.replace('48000000',"+repr(str(delay))+")\nexec(compile('MODE='")
if label=='forced-context':
 diagnostic="""
 def supply_context(uc,pc,n,d):
  e=uc.reg_read(UC_M68K_REG_A3);f=result.get('delayed_note_fixture')
  if f and hex(e)==f['event'] and generations[e]==f['generation']:
   uc.mem_write(BSS+32+(e-0x4199da94)//72*4,u32(0x800040bd))
   result['diagnostic_metadata_injection']={'event':hex(e),'generation':generations[e],'word':'0x800040bd','site':hex(pc),'not_natural_capture':True}
 s.at(0x4009de46,supply_context)
"""
 source=source.replace("exec(compile('MODE='", "source=source.replace(\" generations=collections.Counter();pending={};delayed=False\",\" generations=collections.Counter();pending={};delayed=False\\n\"+"+repr(diagnostic)+")\nexec(compile('MODE='")
source=source.replace("exec(compile('MODE='", "source=source.replace(\"session.tap(session.code('2'),hold_ms=50,after_ms=40)\",\"session.tap(session.code('1'),hold_ms=50,after_ms=40)\")\nsource=source.replace(\" session.press(session.code('PTN'));session.run_ms(40)\",\" session.release(session.code('1'));session.press(session.code('PTN'));session.run_ms(40)\")\nstart=source.index(\" for t in ('T1','T2','T3','T4'):\")\nend=source.index(\" session.press(session.code('PTN'));session.run_ms(40)\",start) if \" session.press(session.code('PTN'));session.run_ms(40)\" in source[start:] else source.index(\" session.release(session.code('1'));session.press(session.code('PTN'));session.run_ms(40)\",start)\nsource=source[:start]+\" session.run_ms(100);mark('source playback before request')\\n\"+source[end:]\nexec(compile('MODE='")
preparation="""
 def select_pattern(number):
  session.press(session.code('PTN'));session.run_ms(30)
  session.tap(session.code(str(number)),hold_ms=30,after_ms=30)
  session.release(session.code('PTN'));session.run_ms(150)
 def combo(button):
  session.press(session.code('FUNC'));session.run_ms(30)
  session.tap(session.code(button),hold_ms=40,after_ms=40)
  session.release(session.code('FUNC'));session.run_ms(150)
 select_pattern(2);copy_source=rd(session.m.uc,0x41342150)
 actual_old=copy_source
 result['native_pattern_preparation']={'old_backing':hex(actual_old),'native_selection':True,'copy_paste_panel_actions':False}
 result['root_scale_fixture']={'old_backing':hex(actual_old),'new_backing':'0x407b00cc','old_root':61,'old_raw_scale':0,'new_root':59,'new_raw_scale':5,'metadata_injection':False}
 for track in range(4):
  session.m.uc.mem_write(0x407b00cc+track*0x3d0+0x3cb,bytes([59]))
  session.m.uc.mem_write(0x407b00cc+track*0x3d0+0x3ce,bytes([5]))
  session.m.uc.mem_write(actual_old+track*0x3d0+0x3cb,bytes([61]))
  session.m.uc.mem_write(actual_old+track*0x3d0+0x3ce,bytes([0]))
"""
source=source.replace("exec(compile('MODE='", "source=source.replace(\" mi.attach(session.m,session.ips);\", "+repr(preparation)+"+\"\\n mi.attach(session.m,session.ips);\")\nexec(compile('MODE='")
exec(compile(source,'queued-arp-crossing','exec'))

