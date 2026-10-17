"""Fail-closed initializer guards in the native engine; no firmware changes."""
import pathlib,json
exec(pathlib.Path('work/test-native-arp-overlays.py').read_text().split('def run(mode):')[0])
from emu.harness import call
startup=json.loads(pathlib.Path('work/native-overlay-startup.json').read_text());INIT=startup['initializer'];TRAMP=startup['trampoline']
result={'cases':[],'firmware_modified':False,'failure':None,'limits':['Invalid guard tests begin in a settled restored native snapshot with explicit private metadata.','Fail-closed spin is not a recovery continuation; it masks interrupts and does not return.','Successful cold initialization is covered in the separate startup-through-playback run.']}
for case in ['wrong_argument','null_pointer','bad_magic','bad_version','bad_size']:
 session=None
 try:
  def installed(s):
   uc=s.m.uc;s.m.ensure(RAM);uc.mem_write(RAM,blob);s.m.install_isa_patches_scoped(blob,RAM)
   uc.mem_write(PTR,bytes(0xb74));uc.mem_write(PTR,u32(BSS-0x14100));uc.mem_write(BSS,struct.pack('>IIII',0x534c4332,2,0xb70,1))
   if case=='null_pointer':uc.mem_write(PTR,u32(0))
   if case=='bad_magic':uc.mem_write(BSS,u32(0))
   if case=='bad_version':uc.mem_write(BSS+4,u32(3))
   if case=='bad_size':uc.mem_write(BSS+8,u32(0xb74))
  session=Session(paths.gui,syx=str(SYX),ddr=DDR,on_machine=installed);uc=session.m.uc
  stock_hits=[];session.at(0x400f050e,lambda uc,a,n,d:stock_hits.append(hex(a)))
  owner_before=rd(uc,0x4199d590);pool_before=bytes(uc.mem_read(0x4199da94,128*72));meta_before=bytes(uc.mem_read(PTR,0xb74))
  session.m.ensure(0x47fdff00);call(session.m,INIT,[0x9f if case=='wrong_argument' else 0x9e],stack_top=0x47fdff00,limit=300)
  pc=uc.reg_read(UC_M68K_REG_PC)
  checks={'terminal_spin':pc==TRAMP-2,'interrupts_masked':uc.reg_read(UC_M68K_REG_SR)&0x0700==0x0700,'no_stock_initializer_entry':not stock_hits,'stock_owner_unchanged':rd(uc,0x4199d590)==owner_before,'stock_pool_unchanged':bytes(uc.mem_read(0x4199da94,128*72))==pool_before,'metadata_unchanged':bytes(uc.mem_read(PTR,0xb74))==meta_before}
  result['cases'].append({'case':case,'pc':hex(pc),'checks':checks});assert all(checks.values()),(case,checks)
 except BaseException as exc:
  result['failure']={'case':case,'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()};print(result['failure']['traceback']);break
 finally:
  if session:session.close()
pathlib.Path('outputs/Digitone-native-startup-guard-results.json').write_text(json.dumps(result,indent=2))
print('Native startup guard cases:',len(result['cases']),'failure:',result['failure'])
