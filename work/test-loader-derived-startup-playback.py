"""Actual loader machine -> application initializer -> guest snapshots -> playback."""
import pathlib,sys,time,json,traceback,inspect,hashlib
sys.path[:0]=['work/emulator-deps','work/upstream/digiemu']
from emu import bootrom,longrun,harness,dspboot
from unicorn.m68k_const import *
# Build the ephemeral extension and observers from the tested continuity probe.
pre=pathlib.Path('work/test-continuous-loader-copier.py').read_text().split('\ntry:\n')[0]
exec(compile(pre,'loader-fixture-preparation','exec'))
LOADER_MAIN=main;LOADER_BLOB=blob;LOADER_META=out;LOADER_HANDLES=[];LOADER_FLASH=bytes(flash)
realMachine=harness.Machine
def recordedMachine(*args,**kwargs):
 m=realMachine(*args,**kwargs);add=m.uc.hook_add
 def recording(*args,**kwargs):
  handle=add(*args,**kwargs);LOADER_HANDLES.append(handle);return handle
 m.uc.hook_add=recording;m._original_hook_add=add;return m
harness.Machine=recordedMachine
try:
 LOADER_RESULT=bootrom.boot(syx,bootstrap,LOADER_MAIN,limit=300000000,chunk=10000000,on_machine=install,trace=trace,ui_card=8,straps={0xec09401b:8},groups=7)
finally:harness.Machine=realMachine
assert LOADER_RESULT.reached==0x400004e8 and LOADER_RESULT.main_os_matches and not LOADER_RESULT.flash_writes
bootrom.save_handoff(LOADER_RESULT,'work/loader-derived-entry.handoff')
LOADER_MACHINE=LOADER_RESULT.m;uc=LOADER_MACHINE.uc
def cpu_state(m):
 return {'regs':{str(reg):m.uc.reg_read(reg) for reg in list(range(UC_M68K_REG_D0,UC_M68K_REG_D0+8))+list(range(UC_M68K_REG_A0,UC_M68K_REG_A0+8))+[UC_M68K_REG_SR,UC_M68K_REG_PC]},'controls':dict(m.ctlregs)}
LOADER_STATE=cpu_state(LOADER_MACHINE);LOADER_MMIO=dict(LOADER_MACHINE.mmio)
# Remove bootstrap-only device hooks before installing the application models.
# Constructor memory-map hooks remain. No CPU, control, SRAM or DDR reset.
for handle in LOADER_HANDLES:
 try:uc.hook_del(handle)
 except Exception:pass
uc.hook_add=LOADER_MACHINE._original_hook_add;LOADER_MACHINE.halt_vec=None
# The native budget hook is installed by C, outside hook_add recording.
# Leaving its exhausted counter live stops every later cold-boot chunk.
old_stepper=getattr(LOADER_MACHINE,'_fast_stepper_obj',None)
if old_stepper is not None and old_stepper._native is not None:
 # hook_del removes the C hook before attempting the Python callback lookup;
 # native-only hooks have no corresponding entry in that callback map.
 try:uc.hook_del(old_stepper._native.hook.value)
 except KeyError:pass
del LOADER_MACHINE._fast_stepper_obj
original_dsp_flash=dspboot.build_flash
dspboot.build_flash=lambda *args,**kwargs:LOADER_FLASH
original_run=dspboot.run
code=inspect.getsource(original_run)
assert code.count('m = Machine(ddr=ddr)')==1
code=code.replace('m = Machine(ddr=ddr)','m = LOADER_MACHINE')
code=code.replace('m.load(main_img, MAIN_LOAD)',"assert bytes(m.uc.mem_read(MAIN_LOAD,len(LOADER_MAIN)))==LOADER_MAIN")
code=code.replace('m.uc.reg_write(UC_M68K_REG_SR, 0x2700)','assert cpu_state(m)==LOADER_STATE')
code=code.replace('m.uc.reg_write(UC_M68K_REG_A7, 0x40800000)','assert m is LOADER_MACHINE')
code=code.replace('start_pc = profile.entry','start_pc = LOADER_RESULT.reached')
namespace=dict(dspboot.__dict__);namespace.update(LOADER_MACHINE=LOADER_MACHINE,LOADER_MAIN=LOADER_MAIN,LOADER_STATE=LOADER_STATE,LOADER_RESULT=LOADER_RESULT,cpu_state=cpu_state)
exec(compile(code,'application-models-on-loader-machine','exec'),namespace);dspboot.run=namespace['run']
LOADER_COLD_SOURCE=pathlib.Path('work/test-native-cold-arp.py').read_text()
lo=LOADER_COLD_SOURCE.index(" if stage=='ladder':");hi=LOADER_COLD_SOURCE.index(" else:\n  assert bytes",lo)
LOADER_COLD_SOURCE=LOADER_COLD_SOURCE[:lo]+''' if stage=='ladder':
  assert m is LOADER_MACHINE and cpu_state(m)==LOADER_STATE
  assert bytes(uc.mem_read(base,len(LOADER_MAIN)))==LOADER_MAIN
  assert bytes(uc.mem_read(RAM,0x20000))==bytes(0x20000)
  rec['entry_flags']=hex(LOADER_RESULT.boot_flags)+' from executed loader'
  report['loader']={'entry':hex(LOADER_RESULT.reached),'main_matches':LOADER_RESULT.main_os_matches,'flags':hex(LOADER_RESULT.boot_flags),'controls':{hex(k):hex(v) for k,v in LOADER_RESULT.m.ctlregs.items()},'same_machine_into_initializer':True,'hooks_removed':len(LOADER_HANDLES),'flash_writes':LOADER_RESULT.flash_writes,'image_sha256':hashlib.sha256(LOADER_MAIN).hexdigest(),'image_bytes':len(LOADER_MAIN),'model_mmio_changes':{hex(k):{'loader':hex(LOADER_MMIO.get(k,0)),'application':hex(v)} for k,v in m.mmio.items() if LOADER_MMIO.get(k)!=v},'limits':['Serial reset hardware represented by loaded bootstrap SRAM.','Bootstrap device hooks replaced by application device models at MAIN entry; CPU, control, SRAM and DDR state retained.','Intro, settle and playback use guest snapshots in fresh engines; this is guest-state continuity, not one engine throughout.','Flash-read HLE and storage/semaphore/timer shortcuts remain modeled.','Playback changes root/scale in a labeled test fixture; it does not prove natural context capture.','Physical cache, DMA and DDR coherence remain unverified.']}
''' +LOADER_COLD_SOURCE[hi:]
LOADER_COLD_SOURCE=LOADER_COLD_SOURCE.replace('bytes([0xa5])','bytes([0])')
LOADER_COLD_SOURCE=LOADER_COLD_SOURCE.replace("'starts_at':'MAIN OS application entry; pre-OS loader is not executed'","'starts_at':'Executed full loader, retaining the same machine into application initialization'")
LOADER_COLD_SOURCE=LOADER_COLD_SOURCE.replace('work/native-cold-arp-emulator','work/loader-derived-arp-emulator')
LOADER_COLD_SOURCE=LOADER_COLD_SOURCE.replace("  run('scale-fixture')","  run('scale-fixture')")
wrapper=pathlib.Path('work/test-fast-table-cold-startup.py').read_text()
wrapper=wrapper.replace("source=pathlib.Path('work/test-native-cold-arp.py').read_text()","source=LOADER_COLD_SOURCE")
wrapper=wrapper.replace('outputs/Digitone-fast-table-cold-startup.json','outputs/Digitone-loader-derived-startup-playback.json')
# Add read witnesses to the playback fixture; all hooks/image/header must be
# restored from startup snapshots, rather than reinstalled by the host.
needle="source=source.replace(\" report['passed']=True\""
pos=wrapper.index(needle)
extra=r'''
source=source.replace(" assert report['runs'][0]['quantize_calls']", " assert len(report['runs'][0]['table_reads'])==len(report['runs'][0]['quantize_calls'])\n assert report['runs'][0]['table_reads']\n assert report['runs'][0]['quantize_calls']")
'''
wrapper=wrapper[:pos]+extra+wrapper[pos:]
from emu.session import Session
from unicorn import UC_HOOK_MEM_READ
original_session_init=Session.__init__
def observed_session_init(self,*args,**kwargs):
 original_session_init(self,*args,**kwargs)
 result=report['runs'][-1];result['table_reads']=[]
 def read(uc,access,address,n,value,d):
  pc=uc.reg_read(UC_M68K_REG_PC)
  assert layout['quantize']['address']<=pc<layout['quantize']['address']+178
  assert n==1 and bytes(uc.mem_read(address,n))==blob[address-RAM:address-RAM+n]
  result['table_reads'].append({'pc':hex(pc),'address':hex(address),'size':n,'value':bytes(uc.mem_read(address,n)).hex()})
 self.m.uc.hook_add(UC_HOOK_MEM_READ,read,begin=RAM+1904,end=RAM+2323)
Session.__init__=observed_session_init
pathlib.Path('work/loader-derived-transform-audit.py').write_text(LOADER_COLD_SOURCE)
try:exec(compile(wrapper,'loader-derived-startup-playback','exec'))
finally:
 dspboot.run=original_run;Session.__init__=original_session_init
 dspboot.build_flash=original_dsp_flash
 if 'report' in globals():
  report['code_bytes']=len(blob)
  report['loader']['flash_sha256']=hashlib.sha256(LOADER_FLASH).hexdigest()
  report['loader']['flash_preserved_in_application_models']=True
  report['elapsed_scope']='elapsed_seconds covers application startup and playback; loader execution occurs before that timer'
  report['diagnostic_end']={'pc':hex(LOADER_MACHINE.uc.reg_read(UC_M68K_REG_PC)),'SR':hex(LOADER_MACHINE.uc.reg_read(UC_M68K_REG_SR)),'controls':{hex(k):hex(v) for k,v in LOADER_MACHINE.ctlregs.items()}}
  persist()
