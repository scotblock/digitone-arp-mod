"""Readable handoff runner: inherited startup hooks, optional arp-enabled receiver."""
import pathlib
p=pathlib.Path;s=p('work/test-cache-context-fresh-rendered.py').read_text()
s=s.replace('work/indexed-context-environment.py','work/cache-context-environment.py').replace('outputs/Digitone-indexed-context-startup-playback.json','outputs/Digitone-cache-context-startup-playback.json')
s=s.replace('import pathlib,json,struct,collections,traceback,time','import pathlib,json,struct,collections,traceback,time,os')
s=s.replace("OUT=pathlib.Path('outputs/Digitone-indexed-context-handoff-cache-context-fresh-settings.json')", "CLONE=os.environ.get('CLONE_RECEIVING')=='1'\nLIVE=os.environ.get('FRESH_LIVE')=='1'\nNATIVE_COPY=os.environ.get('NATIVE_PATTERN_COPY')=='1'\nOUT=pathlib.Path('outputs/Digitone-cache-startup-handoff'+('-receiving-arp' if CLONE else '')+('-fresh-live' if LIVE else '')+('-native-pattern-copy' if NATIVE_COPY else '')+'.json')")
s=s.replace(' s.m.install_isa_patches_scoped(blob[:1892],RAM)',' s.m.install_isa_patches_scoped(blob[:1892],RAM);s.m.install_isa_patches_scoped(blob[2368:],RAM+2368)')
lo=s.index(" if CACHE_MODE=='fixed':");hi=s.index(' def cache_build(',lo)
s=s[:lo]+''' build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
 for site,opcode,target in [(0x4009344e,'4ef9',build['first_copy_address']),(0x40093892,'4eb9',build['copy_address'])]:
  assert bytes(uc.mem_read(site,6))==bytes.fromhex(opcode)+u32(target)
 result['PC_runtime_extension_installed']=False;result['helper_reinjected']=False
 result['inherited_hook_checks']=True
'''+s[hi:]
# Restore contrasting source settings and 3-second queue delay.
s=s.replace('0x407c61e9+track*0x3d0+0x3cb,bytes([59])','0x407c61e9+track*0x3d0+0x3cb,bytes([61])')
s=s.replace('0x407c61e9+track*0x3d0+0x3ce,bytes([5])','0x407c61e9+track*0x3d0+0x3ce,bytes([0])')
s=s.replace('actual_old+track*0x3d0+0x3cb,bytes([59])','actual_old+track*0x3d0+0x3cb,bytes([61])').replace('actual_old+track*0x3d0+0x3ce,bytes([5])','actual_old+track*0x3d0+0x3ce,bytes([0])')
s=s.replace("'old_root':59,'old_raw_scale':5,'new_root':59", "'old_root':61,'old_raw_scale':0,'new_root':59")
s=s.replace('after=(before+0)&0xffffffff','after=(before+96000000)&0xffffffff').replace("'added_timer_ticks':0","'added_timer_ticks':96000000")
target=' for track in range(4):\n  session.m.uc.mem_write(0x407c61e9'
assert target in s
s=s.replace(target,''' if CLONE:
  # Receiving pattern data fixture, while stopped, preserving its index.
  src=0x407c61e9;dst=0x407b00cc;n=0x16119
  original_index=bytes(session.m.uc.mem_read(dst+n,4))
  session.m.uc.mem_write(dst,bytes(session.m.uc.mem_read(src,n)))
  assert bytes(session.m.uc.mem_read(dst+n,4))==original_index
  result['receiving_pattern_fixture']={'source':hex(src),'destination':hex(dst),'copied_bytes':n,'index_preserved':True,'event_fields_injected':False,'context_metadata_injected':False}
  for t in range(4):
   session.m.uc.mem_write(dst+t*0x3d0+0x3cb,bytes([59]));session.m.uc.mem_write(dst+t*0x3d0+0x3ce,bytes([5]))
'''+target,1)
s=s.replace(' actual_old=copy_source', ''' if NATIVE_COPY:
  for t in range(4):
   session.m.uc.mem_write(copy_source+t*0x3d0+0x3cb,bytes([59]));session.m.uc.mem_write(copy_source+t*0x3d0+0x3ce,bytes([5]))
  combo('RECORD');session.release(session.code('1'));select_pattern(1);combo('STOP')
  pasted=rd(session.m.uc,0x41342150)
  result['native_copy_paste_fixture']={'copy_from':hex(copy_source),'paste_to':hex(pasted),'via_panel':True,'transport_stopped_during_preparation':True,'root':59,'raw':5,'metadata_injected':False}
  assert pasted==0x407b00cc,'native paste destination was not pattern 1'
  for t in range(4):
   session.m.uc.mem_write(copy_source+t*0x3d0+0x3cb,bytes([61]));session.m.uc.mem_write(copy_source+t*0x3d0+0x3ce,bytes([0]))
  session.release(session.code('2'));select_pattern(2)
  assert rd(session.m.uc,0x41342150)==copy_source,'native selection did not return to pattern 2'
 actual_old=copy_source''')
s=s.replace(" mark('after actual transition')", """ mark('after actual transition')
 if LIVE:
  send_midi([0xb0|channel,64,0]);session.release(session.code('PTN'));session.release(session.code('1'))
  session.tap(session.code('T3'),hold_ms=60,after_ms=60)
  result['fresh_live_input_fixture']={'note':60,'auto_channel_zero_based':channel,'target_selected_by_panel':'T3','metadata_injection':False,'event_eligibility_injection':False,'transport_stopped':False}
  mark('before fresh live note');send_midi([0x90|channel,60,100]);mark('fresh live note sent')
""")
s=s.replace(" session.tap(session.code('STOP'),hold_ms=30,after_ms=100)"," if LIVE:send_midi([0x80|channel,60,0])\n session.tap(session.code('STOP'),hold_ms=30,after_ms=100)")
p('work/test-cache-startup-handoff.py').write_text(s)
print('Inherited-startup handoff runner generated')
