"""Existing cycle-aware controls using loader-derived guest state, no reinjection."""
import pathlib,os,hashlib
source=pathlib.Path('work/isolate-first-stale-read.py').read_text()
source=source.replace('exec(p)\n',"""exec(p)
from emu import bootstrap as bs
from unicorn import UC_HOOK_MEM_READ
blob=pathlib.Path('work/fast-pitch-overlay.bin').read_bytes()
paths=ExperimentalPaths(str(pathlib.Path('work/loader-derived-arp-emulator').resolve()),SYX.name,paths.devices_dir)
os.environ.update(paths.env())
startup_provenance=json.loads(pathlib.Path('outputs/Digitone-loader-derived-startup-playback.json').read_text())
assert startup_provenance['passed'] and startup_provenance['loader']['same_machine_into_initializer']
# Preserve the same ephemeral flash layout used by the loader/startup run.
# Preparing bytes does not execute a loader or create an installable image.
pre=pathlib.Path('work/test-continuous-loader-copier.py').read_text().split('originalspin=longrun.spin')[0]
flash_namespace={};exec(compile(pre,'ephemeral-flash-fixture','exec'),flash_namespace)
assert hashlib.sha256(flash_namespace['main']).hexdigest()==startup_provenance['loader']['image_sha256']
from emu import dspboot
loader_flash=bytes(flash_namespace['flash'])
dspboot.build_flash=lambda *args,**kwargs:loader_flash
""",1)
lo=source.index("  if mode in ('all','all_fixed','context_only','sham'):")
hi=source.index("  rec['clock_source']=",lo)
source=source[:lo]+'''  assert bytes(uc.mem_read(RAM,len(blob)))==blob
  assert rd(uc,PTR)==BSS-0x14100 and list(struct.unpack('>IIII',uc.mem_read(BSS,16)))==[0x534c4332,2,0xb70,1]
  assert m.ctlregs.get(2)==0xa50ce100 and m.ctlregs.get(4)==0x4007e020
  rec['startup_provenance']={'snapshot':str(paths.gui),'snapshot_sha256':hashlib.sha256(pathlib.Path(paths.gui).read_bytes()).hexdigest(),'loader_image_sha256':startup_provenance['loader']['image_sha256'],'helper_sha256':hashlib.sha256(bytes(uc.mem_read(RAM,len(blob)))).hexdigest(),'initial_controls':{hex(k):hex(v) for k,v in m.ctlregs.items()},'helper_and_header_reinjected':False,'hook_control_changes':[]}
  m.install_isa_patches_scoped(blob[:1892],RAM)
  rec['_guards_before']=bytes(uc.mem_read(RAM,0x20000)).hex()
  # Full/fixed cases keep every startup-installed hook. Other cases remove
  # selected hooks only for a diagnostic comparison from identical state.
  for pc,name,op,n in specs:
   expected=bytes.fromhex(op)+u32(layout[name]['address'])+bytes.fromhex('4e71')*((n-6)//2)
   assert bytes(uc.mem_read(pc,n))==expected,hex(pc)
   if mode in ('stock','stock_changed','sham') or (mode=='context_only' and name=='pitch_hook'):
    uc.mem_write(pc,stock[pc-base:pc-base+n]);rec['startup_provenance']['hook_control_changes'].append({'pc':hex(pc),'action':'restore stock instructions'})
  if mode=='sham':
   addr=RAM+0xe00;uc.mem_write(addr,stock[0x4009df9a-base:0x4009dfa2-base]+bytes.fromhex('4ef9')+u32(0x4009dfa2));uc.mem_write(0x4009df9a,bytes.fromhex('4ef9')+u32(addr)+bytes.fromhex('4e71'))
   rec['startup_provenance']['hook_control_changes'].append({'pc':'0x4009df9a','action':'sham detour in diagnostic spare bytes'})
  rec['table_reads']=[];rec['unexpected_storage_writes']=[]
  def read_table(uc,access,address,n,value,d):
   pc=uc.reg_read(UC_M68K_REG_PC);assert layout['quantize']['address']<=pc<layout['quantize']['address']+178
   assert n==1 and bytes(uc.mem_read(address,n))==blob[address-RAM:address-RAM+n]
   rec['table_reads'].append({'cycles':session.clock.cycles,'pc':hex(pc),'address':hex(address),'value':bytes(uc.mem_read(address,n)).hex()})
  uc.hook_add(UC_HOOK_MEM_READ,read_table,begin=RAM+1904,end=RAM+2323)
  def storage_write(uc,access,address,n,value,d):
   physical=0x40000000+(address-0x40000000)%DDR
   if not (physical<RAM+0x20000 and RAM<physical+n):return
   pc=uc.reg_read(UC_M68K_REG_PC)
   if PTR<=physical and physical+n<=BSS+0xb70 and RAM<=pc<RAM+1892:return
   rec['unexpected_storage_writes'].append({'pc':hex(pc),'address':hex(address),'size':n})
  for k in range(8):uc.hook_add(UC_HOOK_MEM_WRITE,storage_write,begin=RAM+k*DDR-64,end=RAM+k*DDR+0x20000+63)
''' +source[hi:]
if os.environ.get('LONG_PLAYBACK')=='1':
 heavy=pathlib.Path('work/test-voice-heavy-memory-sensitivity.py').read_text()
 segment=heavy[heavy.index("  session.tap(session.code('KEYBOARD')"):heavy.index('  rec.update(memory_model=')]
 source=source.replace("  mark('prefix ends at 80 ms before keyboard input')\n",segment)
source=source.replace('  rec.update(memory_model=', '''  now=bytes(session.m.uc.mem_read(RAM,0x20000));guard=bytes.fromhex(rec.pop('_guards_before'))
  excluded=set(range(PTR-RAM,BSS+0xb70-RAM))
  if mode=='sham':excluded.update(range(0xe00,0xe00+14))
  rec['storage_checks']={'helper_intact':now[:len(blob)]==blob,'guards_intact':all(now[i]==guard[i] for i in range(len(now)) if i not in excluded),'no_unexpected_guest_writes':not rec['unexpected_storage_writes'],'table_reads_match_quantizer_calls':len(rec['table_reads'])==len(rec['quantizer_calls'])}
  assert all(rec['storage_checks'].values())
  rec.update(memory_model=''',1)
source=source.replace("report={'experiment':", "report={'startup_provenance_source':'outputs/Digitone-loader-derived-startup-playback.json','optimized_build':json.loads(pathlib.Path('work/fast-pitch-build.json').read_text()),'experiment':",1)
# This startup snapshot reaches its first arp pitch around 77 ms, later than
# the former supplied-state fixture. Move diagnostic windows to include it.
source=source.replace('55<=session.now_ms()<=64','70<=session.now_ms()<=80')
source=source.replace('45<=session.now_ms()<=75','45<=session.now_ms()<=85')
source=source.replace('45<=ms<=75','45<=ms<=85')
# Bound this diagnostic counterfactual to each pitch-entry/output interval.
source=source.replace("  session.at(0x4009dfa8,control_pitch)","   rec['pitch_fetch_ablation']['active']=False\n  session.at(0x4009dfa8,control_pitch)")
exec(compile(source,'loader-derived-cycle-timing','exec'))
