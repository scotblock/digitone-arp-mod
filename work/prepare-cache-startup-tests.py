"""Generate PC-only bootstrap and timing probes with both cache-copy hooks."""
import pathlib
p=pathlib.Path
hooks="""
cache_build=json.loads(pathlib.Path('work/cache-context-build.json').read_text())
for site,opcode,target in [(0x4009344e,'4ef9',cache_build['first_copy_address']),(0x40093892,'4eb9',cache_build['copy_address'])]:
 expected=bytes.fromhex('4e914fef000c' if site==0x4009344e else '4eb9400ec23c')
 assert bytes(main[site-BASE:site-BASE+6])==expected
 main[site-BASE:site-BASE+6]=bytes.fromhex(opcode)+u32(target)
"""
fixture=p('work/test-continuous-loader-copier.py').read_text().replace('work/fast-pitch-overlay.bin','work/cache-context-overlay.bin')
fixture=fixture.replace('main.extend(copier+bytes(256-len(copier))+blob);main=bytes(main)',hooks+'\nmain.extend(copier+bytes(256-len(copier))+blob);main=bytes(main)')
p('work/cache-loader-fixture.py').write_text(fixture)
startup=p('work/test-indexed-context-startup.py').read_text().replace('indexed-context','cache-context').replace('indexed-loader','cache-loader')
startup=startup.replace("text=text.replace('work/loader-derived-entry.handoff'", "text=text.replace('work/test-continuous-loader-copier.py','work/cache-loader-fixture.py')\ntext=text.replace('work/loader-derived-entry.handoff'")
startup=startup.replace("exec(compile(text,'indexed-loader-startup','exec'))", "exec(compile(text,'cache-loader-startup','exec'))")
# The wrapper embeds a previous length assertion and executable-prefix scan.
startup=startup.replace("exec(compile(text,", "text=text.replace(\"try:exec(compile(wrapper,\", \"wrapper=wrapper.replace('assert len(blob)==2324','assert len(blob)==2564')\\nwrapper=wrapper.replace('m.install_isa_patches_scoped(blob[:1892],RAM)','m.install_isa_patches_scoped(blob[:1892],RAM);m.install_isa_patches_scoped(blob[2368:],RAM+2368)')\\ntry:exec(compile(wrapper,\")\nexec(compile(text,")
p('work/test-cache-context-startup.py').write_text(startup)
env=p('work/indexed-context-environment.py').read_text().replace('indexed-context','cache-context').replace('indexed-loader','cache-loader').replace('work/test-continuous-loader-copier.py','work/cache-loader-fixture.py')
p('work/cache-context-environment.py').write_text(env)
timing=p('work/run-indexed-context-timing-case.py').read_text().replace('indexed-context','cache-context').replace('indexed-loader','cache-loader')
timing=timing.replace("exec(compile(source,'cache-context-timing-case','exec'))",'''source=source.replace('work/test-continuous-loader-copier.py','work/cache-loader-fixture.py')
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
source=source.replace(needle,extra+'\\n'+needle)
exec(compile(source,'cache-context-timing-case','exec'))''')
p('work/run-cache-context-timing-case.py').write_text(timing)
print('PC startup, environment and timing probes generated')
