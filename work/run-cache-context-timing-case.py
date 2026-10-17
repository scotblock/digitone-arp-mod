"""Cycle-aware controls from compact helper's actual loader-derived startup."""
import pathlib
source=pathlib.Path('work/run-loader-timing-case.py').read_text()
source=source.replace('work/fast-pitch-overlay.bin','work/cache-context-overlay.bin')
source=source.replace('work/loader-derived-arp-emulator','work/cache-loader-derived-arp-emulator')
source=source.replace('outputs/Digitone-loader-derived-startup-playback.json','outputs/Digitone-cache-context-startup-playback.json')
source=source.replace("flash_namespace={};exec", "pre=pre.replace('work/fast-pitch-overlay.bin','work/cache-context-overlay.bin')\nflash_namespace={};exec")
source=source.replace('work/fast-pitch-build.json','work/cache-context-build.json')
source=source.replace("exec(compile(source,'loader-derived-cycle-timing','exec'))", "if os.environ.get('EXTENDED_HOLD')=='1':source=source.replace('  for i in range(16):','  for i in range(32):')\nexec(compile(source,'loader-derived-cycle-timing','exec'))")
source=source.replace('work/test-continuous-loader-copier.py','work/cache-loader-fixture.py')
source=source.replace("m.install_isa_patches_scoped(blob[:1892],RAM)","m.install_isa_patches_scoped(blob[:1892],RAM);m.install_isa_patches_scoped(blob[2368:],RAM+2368)")
source=source.replace('RAM<=pc<RAM+1892','RAM<=pc<RAM+len(blob)')
needle="  rec['table_reads']=[];rec['unexpected_storage_writes']=[]"
extra="""
  build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
  rec['cache_copy_calls']=[]
  for site,opcode,target in [(0x4009344e,'4ef9',build['first_copy_address']),(0x40093892,'4eb9',build['copy_address'])]:
   assert bytes(uc.mem_read(site,6))==bytes.fromhex(opcode)+u32(target)
   if mode in ('stock','stock_changed','sham'):
    uc.mem_write(site,stock[site-base:site-base+6]);rec['startup_provenance']['hook_control_changes'].append({'pc':hex(site),'action':'restore stock cache copy'})
   def copy_seen(uc,pc,n,d):
    sp=uc.reg_read(UC_M68K_REG_A7)
    rec['cache_copy_calls'].append({'pc':hex(pc),'ms':session.now_ms(),'destination':hex(rd(uc,sp)),'source':hex(rd(uc,sp+4))})
   session.at(site,copy_seen)
"""
source=source.replace(needle,extra+'\n'+needle)
exec(compile(source,'cache-context-timing-case','exec'))

