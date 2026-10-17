"""Actual cache construction/copy and transition with PC-only machine-code fix."""
import pathlib,os,json
src=pathlib.Path('work/test-queued-arp-context-crossing.py').read_text()
probe=os.environ.get('CACHE_CONTEXT_MODE','observe');assert probe in ['observe','fixed']
refresh=os.environ.get('CACHE_REFRESH')=='1'
src=src.replace("suffix='queued-arp-crossing'+('' if label=='natural' else '-'+label)","suffix='cache-context-'+"+repr(probe)+"+('-no-delay' if label=='no-delay' else '')+"+repr('-refresh' if refresh else ''))
addition='''
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
'''
# Add after startup checks and before the storage guard is sampled.
if refresh:
 phase='''
 # A second native handoff rebuilds the same cache slot from different settings.
 b=int(result['native_pattern_preparation']['old_backing'],16)
 for t in range(4):
  session.m.uc.mem_write(b+t*0x3d0+0x3cb,bytes([59]));session.m.uc.mem_write(b+t*0x3d0+0x3ce,bytes([5]))
 result['refresh_root_scale_fixture']={'backing':hex(b),'root':59,'raw_scale':5,'metadata_injection':False}
 session.tap(session.code('STOP'),hold_ms=40,after_ms=100)
 session.release(session.code('2'));session.release(session.code('PTN'));session.run_ms(100)
 mark('refresh request');select_pattern(2);mark('refresh completed observation')
 assert rd(session.m.uc,0x41342150)==b, 'second native pattern selection did not complete'
 session.tap(session.code('PLAY'),hold_ms=40,after_ms=100)
 session.run_ms(1800);mark('fresh cached arp playback')
'''
 target=" session.tap(session.code('STOP'),hold_ms=30,after_ms=100)"
 nested="source=source.replace("+repr(target)+","+repr(phase+'\n'+target)+")\nexec(compile('MODE='"
 src=src.replace("exec(compile(source,'queued-arp-crossing','exec'))", "source=source.replace(\"exec(compile('MODE='\", "+repr(nested)+")\nexec(compile(source,'queued-arp-crossing','exec'))")
src=src.replace("exec(compile(source,'queued-arp-crossing','exec'))", "source=source.replace(\" result['_guards']=bytes(uc.mem_read(RAM,0x20000)).hex()\", "+repr(addition)+"+\"\\n result['_guards']=bytes(uc.mem_read(RAM,0x20000)).hex()\")\nsource=source.replace('RAM<=pc<RAM+1892','RAM<=pc<RAM+len(blob)')\nsource=source.replace('def install(s):','def install(s):\\n global blob')\nexec(compile('CACHE_MODE='+"+repr(repr(probe))+"+'\\n'+source,'cache-context-crossing','exec'))")
exec(compile(src,'cache-context-runner','exec'))



